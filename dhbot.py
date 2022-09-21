import random
import json
import pathlib
import discord
import time
import sqlutils
import mysql.connector
from discord.ext import commands


HELP = "!tochka <уровень> <тип> <заточка> <камни>\nТипы:\ntype-n - белое\ntype-a - фиолетовое\ntype-b - интовое\ntype-c стринт\ntype-l - леон\ntype-r - реликт\ntype-s - антиграв\nКамни от t0 - без камня до t5, 4 штуки через '-'\nПример шанса заточки 55 леона на +2 с сетом камней т4:\n!tochka 55 type-l 2 t4-t4-t4-t4"

ERROR = "Неверное использование команды. Попробуй !tochka help"

types = ['type-n','type-a','type-b','type-c','type-l','type-r','type-s']
types_m = ['белого','фиолетового','инты','стринты','леона','реликта','антиграва']
types_ch = [[1000,750,500,250,100,50,3],[500,400,300,200,80,50,10],[1000,750,600,350,100,50,1],[1000,750,500,250,100,50,1],[800,600,400,200,120,40,1],[950,750,600,400,89,16,1],[640,480,320,160,96,32,3]]
types_destr = [[0,0,0,0,1600,3200,6400],[1000,1500,2000,2500,3000,3500,4000],[0,0,0,1000,2250,3500,5750],[0,750,1125,1500,2375,3250,4625],[10000,10000,10000,10000,10000],[2400,3940,6170,6790,7470,8220,9040],[7000,7700,8470,9320,10000,10000,10000]]
types_vilet = [[0,0,0,0,2000,4000,8000],[1000,1500,2000,2500,3000,3500,4000],[0,0,0,2000,4500,7000,9500],[0,3000,4500,6000,9500,9500,9500],[0,3600,5400,7200,9500,9500,9500],[0,3600,5400,7200,9500,9500,9500],[0,7300,9500,9500,9500,9500,9500],[0,4300,6400,8600,9500,9500,9500]]

gems = ['t0','t1','t2','t3','t4','t5','t6']
gems_m = ['',':one:',':two:',':three:',':four:',':five:',':six:']
gems_ch = [0.125,0.25,0.5,1.0,1.5,2.3,2.7]
    
#def read_token():
    #with open("token.txt", "r") as f:
        #lines = f.readlines()
        #return lines[0].strip()

def read_token():
    with open("data.txt", "r") as f:
        lines = f.read().rstrip()
        return lines[0]

TOKEN = read_token()

help_message = "Список команд:\n**!tochka** - узнать шанс заточки предметов на PvPWar Refresh (**!tochka help** - подробная информация о команде)\n**!item** - положить предмет в модификатор, после команды через пробел можно указать конкретный предмет, который вы хотите заточить, используя emoji. Также существует сокращенная версия команды - **!i**\nБольшая просьба не оставлять предметы в модификаторы, он один на всех\n**!talika** - всунуть талику невежества в модификатор. (Сокращенная версия - **!t**)\n**!gem** - всунуть комплект т4 в модификатор. (Сокращенная версия - **!g**)\n**!modify** - заточить предмет, в случае сгорания предмета вам будет выдана случайная коробка, чем выше заточка - тем выше шанс получить большую коробку. (Сокращенная версия - **!m**)\n**!dance** - потанцевать вокруг модификатора с бубном. Повышает шанс заточки, можно использовать один раз за предмет\n**!mix** - перемешать камни в модификаторе. Повышает шанс заточки, можно использовать один раз за предмет и только при наличии камней в модификаторе\n**!t5** - поменять камни Т4 на Т5. Незначительно повышает шанс заточки и сильно повышает шанс того, что при неудачной заточке оружие не сгорит. На предмет дается один бесплатный комплект Т5, при наличии Т5 в инвентаре - их можно использовать пока не закончатся. Можно использовать только при наличии камней т4 в модификаторе\n**!t6** - поменять камни Т4 на Т6. Увеличивает шанс заточки и полностью убирает шанс сломать предмет, можно использовать только при наличии Т6 в инвентаре\n**!inv** - узнать содержимое инвентаря\n**!box** - открыть коробку. Используется либо с emoji коробок, либо **!box all** - чтобы открыть все коробки, которые есть у вас в инвентаре\n**!top** - посмотреть топ10\n**!status** - узнать какой предмет находится в модификаторе\n**!bank** - узнать содержимое банка (все команды связаные с банком работают только в канале #bank)\n**!store** - положить предмет в банк\n**!remove - убрать предмет из банка**"

bot = commands.Bot(command_prefix='!',case_insensitive=True,strip_after_prefix=True,activity=discord.Game(name='PvPWar Refresh'),allowed_mentions = discord.AllowedMentions(everyone = True))
bot.remove_command("help")

bot.db = None
voteChannel = 920642872456388608
emoji_no = '<:no:920652566189211688>'
emoji_yes = '<:yes:920652565966893116>'

@bot.command(pass_context=True) #разрешаем передавать агрументы
async def help(ctx):
    await ctx.send(embed = getEmbed(help_message,discord.Color.blue()))
    await ctx.message.delete(delay=0.5)

async def checkPerms(ctx):
    if waitForCommand():
        await ctx.message.delete(delay=0.5)
        return True
    if ctx.channel.id !=allowed_id:
        await ctx.send(content=ctx.message.author.mention+" кыш, в этом канале нельзя пользоваться ботом!",delete_after=20)
        await ctx.message.delete(delay=0.5)
        return True
    return False

def waitForCommand():
    ctime = time.time()
    delta = ctime - bot.lastcommand
    if delta>=1.0:
        bot.lastcommand = ctime
        return False
    return True

@bot.command(pass_context=True) #разрешаем передавать агрументы
async def tochka(ctx, *args): #создаем асинхронную фунцию бота
    if await checkPerms(ctx):
        return
    if(len(args)==1 and args[0]=="help"):
        await ctx.send(embed=getEmbed(HELP,discord.Color.dark_orange()))
    elif len(args)!=4 or args[1] not in types or not args[0].isnumeric() or not args[2].isnumeric() or int(args[2]) < 1 or int(args[2])> 7 or not gems_ok(args[3]):
        await ctx.send(embed=getEmbed(ERROR,discord.Color.dark_orange()),delete_after=30)
    else: 
        level = int(args[0])
        stage = int(args[2])-1
        stones = args[3].split('-')
        gemschance = getGemsChance(stones)
        index = types.index(args[1])

        success = round(getBase(types_ch[index][stage],level, gemschance) / 1000.0,2)
        ns = 100.0 - success
        destr = round((ns * (types_destr[index][stage]/ 100.0))/100.0,2)
        nd = (100.0 - destr)/100.0
        #nd = (100.0 - destr)
        vilet = round((ns * nd  * (types_vilet[index][stage]/100.0))/100.0,2)
        nv = (100.0 - vilet)/100.0
        #nv = (100.0 - vilet)
        fail = round(ns * nd * nv,2)

        tit = "Шанс заточки "+types_m[types.index(args[1])]+" "+args[0]+" уровня на +"+args[2]+" с камнями "+gems_m[gems.index(stones[0])]+gems_m[gems.index(stones[1])]+gems_m[gems.index(stones[2])]+gems_m[gems.index(stones[3])]+":"
        message = "Успех: "+str(success)+"%\nУничтожение: "+str(destr)+"%\nВылет: "+str(vilet)+"%\nНеудача: "+str(fail)+"%"
        embed = discord.Embed(title=tit,description=message, color=discord.Color.blue())
        await ctx.send(embed=embed)

def getGemsChance(gem_array):
    chance = 0.0
    for gem in gem_array:
        chance += gems_ch[gems.index(gem)]
    return chance

def getBase(b,l,g):
    base = b * g * 30.0 * 100.0 / (4.0 * l)
    return base

bot.currentitem = "none"
bot.currentowner = '-'
bot.currentownerid = '-'

bot.keen = False

bot.tanec = 0
bot.tfive = 0
bot.tsix = False
bot.mix = 0
bot.currentmod = 0

bot.lastcommand = 0
bot.premium = False

bot.gems_in = [False,False,False,False]
chances = [63.33,53.33,30.0,13.33,6.67,2.2,0.67]
box_chanses = [100.0,75.0,60.0,45.0,25.0,15.0,1.0,1.0]

items = ["<:bowmelf:910857314578362368>","<:bowelf:910858327246905345>","<:staffelf:910858327578267658>","<:staffonehand:910857650189791272>","<:swordelf:910858327481790484>","<:swordmelf:910857287730593803>","<:axes:913303519069618176>","<:pistols:913345501007589376>","<:bow:913345500802068480>","<:spear:913345500491681803>","<:sword:913345501015986196>"]
gems_em = ['<:gemt41:910823297757872138>','<:gemt42:910823297539780619>','<:gemt43:910823297833390130>','<:gemt44:910823298143768607>']
boxes = ['<:smallbox:913322344590737450>','<:mediumbox:913322344506855425>','<:largebox:913321935675490304>']
gems_complects = ['<:tfive:913615358525583432>','<:tsix:913615358777233450>','<:modik24:913615095714693222>']

allowed_id = 911456081417469962
bank_id = 921222192136605716

def getEmbed(message,cl):
    return discord.Embed(description=message,color=cl)

def correctType(tp):
    if tp=="bb":
        return True
    elif tp=="db":
        return True
    elif tp=="mag":
        return True
    elif tp=="jew":
        return True
    elif tp=="res":
        return True
    elif tp=="other":
        return True
    else:
        return False

@bot.command(pass_context = True,aliases=["store","положить"])
async def _store(ctx, *args):
    if ctx.channel.id != bank_id:
        return
    if len(args)<2:
        await ctx.message.delete(delay=0.5)
        return await ctx.send(embed=getEmbed("Неправильное использование команды.\nЧтобы положить в банк предмет - используйте !store или !положить <тип> <предмет>\nВозможные типы:\nbb - предметы полезные для ББшников\ndb - предметы полезные для ДБшников\nmag - предметы полезные для магов\njew - бижа\nres - ресурсы\nother - прочее",discord.Color.red()),delete_after=30)
    if correctType(args[0]) is False:
        await ctx.message.delete(delay=0.5)
        return await ctx.send(embed=getEmbed("Неправильное использование команды.\nЧтобы положить в банк предмет - используйте !store или !положить <тип> <предмет>\nВозможные типы:\nbb - предметы полезные для ББшников\ndb - предметы полезные для ДБшников\nmag - предметы полезные для магов\njew - бижа\nres - ресурсы\nother - прочее",discord.Color.red()),delete_after=30)
    owid = ctx.message.author.id
    name = ctx.message.author.name
    item = ""
    for x in range(1,len(args)):
        item+=args[x]+" "
    sqlutils.storeItem(args[0],name,item,owid)
    await ctx.message.delete(delay=0.5)
    return await ctx.send(embed=getEmbed("**"+name+"** положил(а) в банк ***"+item+"***",discord.Color.green()))

@bot.command(pass_context = True,aliases=["bank","банк"])
async def _bank(ctx, *args):
    if ctx.channel.id != bank_id:
        return
    if len(args)<1:
        await ctx.message.delete(delay=0.5)
        return await ctx.send(embed=getEmbed("Неправильное использование команды.\nЧтобы посмотреть содержимое банка - используйте !bank или !банк <тип>\nВозможные типы:\nbb - предметы полезные для ББшников\ndb - предметы полезные для ДБшников\nmag - предметы полезные для магов\njew - бижа\nres - ресурсы\nother - прочее\nmy - посмотреть ваши предметы",discord.Color.red()),delete_after=30)
    if correctType(args[0]) is True:
        bank = sqlutils.getItemsInBank(args[0])
        if len(bank)>0:
            message = "Предметы в банке по вашему запросу:"
            index = 1
            for item,owner in bank:
                message+="\n**"+str(index)+"**. "+item+" (**"+owner+"**)"
                index+=1
            await ctx.message.delete(delay=0.5)
            return await ctx.send(embed=getEmbed(message,discord.Color.blue()))
        else:
            await ctx.message.delete(delay=0.5)
            return await ctx.send(embed=getEmbed("В банке нет предметов данного типа",discord.Color.red()),delete_after=30)
    elif args[0]=="my":
        bank = sqlutils.getOwnItemsInBank(ctx.message.author.id)
        if len(bank)>0:
            message = "Ваши предметы в банке:"
            for id,item in bank:
                message+="\n#**"+str(id)+"**. "+item
            await ctx.message.delete(delay=0.5)
            return await ctx.send(embed=getEmbed(message,discord.Color.blue()))
        else:
            await ctx.message.delete(delay=0.5)
            return await ctx.send(embed=getEmbed("В банке нет ваших предметов",discord.Color.red()),delete_after=30)
    else:
        await ctx.message.delete(delay=0.5)
        return await ctx.send(embed=getEmbed("Неправильное использование команды.\nЧтобы посмотреть содержимое банка - используйте !bank или !банк <тип>\nВозможные типы:\nbb - предметы полезные для ББшников\ndb - предметы полезные для ДБшников\nmag - предметы полезные для магов\njew - бижа\nres - ресурсы\nother - прочее\nmy - посмотреть ваши предметы",discord.Color.red()),delete_after=30)

@bot.command(pass_context = True,aliases=["remove","убрать"])
async def _remove(ctx, *args):
    if ctx.channel.id != bank_id:
        return
    if len(args)<1:
        await ctx.message.delete(delay=0.5)
        return await ctx.send(embed=getEmbed("Неправильное использование команды.\nЧтобы убрать предмет из банка - используйте !remove id или !убрать id, где id - номер предмета указанный при просмотре содержимого вашего банка (!bank my)",discord.Color.red()),delete_after=30)
    item = sqlutils.getSpecialItem(args[0])
    if len(item)>0:
        for item,oid in item:
            if oid==str(ctx.message.author.id):
                sqlutils.removeItemFromBank(args[0])
                await ctx.message.delete(delay=0.5)
                return await ctx.send(embed=getEmbed("**"+ctx.message.author.name+"** убрал(а) из банка ***"+item+"***",discord.Color.gold()))
            else:
                await ctx.message.delete(delay=0.5)
                return await ctx.send(embed=getEmbed("Вы не можете убрать из банка предмет, который вам не принадлежит",discord.Color.red()),delete_after=30)
    else:
        await ctx.message.delete(delay=0.5)
        return await ctx.send(embed=getEmbed("В банке нет предмета с этим ID",discord.Color.red()),delete_after=30)
    

@bot.command(pass_context = True)
async def vote(ctx, *args):
    if ctx.channel.id == voteChannel:
        if len(args)==0:
            await ctx.message.delete(delay=0.5)
            return
        title_message = "**"+ctx.message.author.name+"** начал(а) голосование:"
        vote_message = ""
        for arg in args:
            vote_message+=arg+" "
        embed = discord.Embed(title=title_message,description=vote_message, color=discord.Color.blue())
        vote_m = await ctx.send(embed=embed)
        await vote_m.add_reaction(emoji_no)
        await vote_m.add_reaction(emoji_yes)
        await ctx.message.delete(delay=0.5)
        await ctx.send('@everyone')



@bot.command(aliases=["item","i"],pass_context=True) #разрешаем передавать агрументы
async def _item(ctx, *args): #создаем асинхронную фунцию бота
    if await checkPerms(ctx):
        return
    arg = ""
    if len(args)==0:
        arg = random.choice(items)
    else:
        arg = args[0]
    if bot.currentitem!="none" or arg not in items:
        if bot.currentitem!="none":
            await ctx.send(embed=getEmbed("В модификаторе уже есть предмет",discord.Color.dark_orange()),delete_after=10)
            await ctx.message.delete(delay=0.5)
        else:
            await ctx.send(embed=getEmbed("Этот предмет ("+arg+") нельзя положить в модификатор",discord.Color.dark_orange()),delete_after=10)
            await ctx.message.delete(delay=0.5)
    else:
        result = sqlutils.isCD(ctx)
        if result!="-":
            await ctx.send(embed=getEmbed("**"+ctx.message.author.name+"**, в вашей сумке нет предметов для заточки, попробуйте через "+result+" сек.",discord.Color.dark_orange()),delete_after=10)
            await ctx.message.delete(delay=0.5)
        else:
            sqlutils.saveCurrent(arg,ctx.message.author.name,bot.currentmod)
            bot.premium = False
            if ctx.message.author.premium_since is not None:
                bot.premium = True
            bot.currentitem = arg
            bot.currentowner = ctx.message.author.name
            bot.currentownerid = ctx.message.author.id
            await ctx.send(embed=getEmbed("**"+ctx.message.author.name +"** засунул в модификатор "+arg,discord.Color.blue()))
            await ctx.message.delete(delay=0.5)
            

@bot.command(pass_context=True)
async def dance(ctx):
    if await checkPerms(ctx):
        return
    if bot.tanec==0:
        bot.tanec = 1
        await ctx.send(embed=getEmbed("**"+ctx.message.author.name+"** танцует с бубном вокруг модификатора",discord.Color.purple()))
        await ctx.message.delete(delay=0.5)
    elif bot.tanec == 1:
        await ctx.send(embed=getEmbed("Кто-то уже потанцевал с бубном, еще один танец всё только испортит.",discord.Color.dark_orange()),delete_after=10)
        await ctx.message.delete(delay=0.5)
    else:
        await ctx.send(embed=getEmbed("**"+ctx.message.author.name+"** достает бубен, начинает танцевать, но спотыкается и падает, сегодня видимо без танцев.",discord.Color.dark_orange()),delete_after=10)
        await ctx.message.delete(delay=0.5)


@bot.command(pass_context=True)
async def t5(ctx):
    if await checkPerms(ctx):
        return
    if True in bot.gems_in and bot.tfive==0 and bot.tsix == False:
        bot.tfive = 1
        await ctx.send(embed=getEmbed("**"+ctx.message.author.name+"** меняет Т4 камни на Т5",discord.Color.purple()))
        await ctx.message.delete(delay=0.5)
    elif True not in bot.gems_in:
        await ctx.send(embed=getEmbed("В модификаторе нет камней, которые можно было бы заменить",discord.Color.dark_orange()),delete_after=10)
        await ctx.message.delete(delay=0.5)
    elif bot.tfive == 1:
        await ctx.send(embed=getEmbed("В модификаторе итак уже камни Т5",discord.Color.dark_orange()),delete_after=10)
        await ctx.message.delete(delay=0.5)
    elif bot.tsix == True:
        await ctx.send(embed=getEmbed("Камни Т6 нельзя заменить на Т5",discord.Color.dark_orange()),delete_after=10)
        await ctx.message.delete(delay=0.5)
    else:
        if sqlutils.getItemFromInventory(ctx.message.author.id,"tfive") == True:
            bot.tfive = 1
            await ctx.send(embed=getEmbed("**"+ctx.message.author.name+"** меняет Т4 камни на Т5",discord.Color.purple()))
            await ctx.message.delete(delay=0.5)
        else:
            await ctx.send(embed=getEmbed("**"+ctx.message.author.name+"**, у вас нет камней Т5",discord.Color.dark_orange()),delete_after=10)
            await ctx.message.delete(delay=0.5)


@bot.command(pass_context=True)
async def mix(ctx):
    if await checkPerms(ctx):
        return
    if True in bot.gems_in and bot.mix == 0:
        bot.mix = 1
        await ctx.send(embed=getEmbed("**"+ctx.message.author.name+"** достает все камни из модификатора, перемешивает их в инвентаре и вставляет обратно в модификатор.",discord.Color.purple()))
        await ctx.message.delete(delay=0.5)
    elif True not in bot.gems_in:
        await ctx.send(embed=getEmbed("В модификаторе нет камней, которые можно было бы перемешать",discord.Color.dark_orange()),delete_after=10)
        await ctx.message.delete(delay=0.5)
    elif bot.mix == 1:
        await ctx.send(embed=getEmbed("Камни уже перемешаны, вы же знаете определение безумия?",discord.Color.dark_orange()),delete_after=10)
        await ctx.message.delete(delay=0.5)
    else:
        await ctx.send(embed=getEmbed("**"+ctx.message.author.name +"** подумал о том, чтобы перемешать камни, но передумал.",discord.Color.dark_orange()),delete_after=10)
        await ctx.message.delete(delay=0.5)


@bot.command(aliases=["talika","t"],pass_context=True) #разрешаем передавать агрументы
async def _talika(ctx): #создаем асинхронную фунцию бота
    if await checkPerms(ctx):
        return
    if bot.keen==False:
        bot.keen = True
        await ctx.send(embed=getEmbed("**"+ctx.message.author.name +"** засунул в модификатор <:nevezha:910817933796724756>",discord.Color.gold()))
        await ctx.message.delete(delay=0.5)
    else:
        await ctx.send(embed=getEmbed("В модификаторе уже есть невежа",discord.Color.dark_orange()),delete_after=10)
        await ctx.message.delete(delay=0.5)


@bot.command(aliases=["gem","g"],pass_context=True) #разрешаем передавать агрументы
async def _gem(ctx,*args): #создаем асинхронную фунцию бота
    if await checkPerms(ctx):
        return
    message = "**"+ctx.message.author.name+ "** засунул в модификатор"
    anygem = False
    if len(args)==0:
        for gem in gems_em:
            index = gems_em.index(gem)
            if bot.gems_in[index]==False:
                bot.gems_in[index] = True
                message += gem
                anygem = True
    for arg in args:    
        if arg in gems_em:
            index = gems_em.index(arg)
            if bot.gems_in[index]==False:
                bot.gems_in[index] = True
                message +=arg
                anygem = True
    if anygem==True:
        await ctx.send(embed=getEmbed(message,discord.Color.dark_blue()))
        await ctx.message.delete(delay=0.5)
    else:
        await ctx.send(embed=getEmbed("В модификаторе либо уже есть эти камни, либо вы пытаетесь вставить туда какую-то хрень",discord.Color.dark_orange()),delete_after=10)
        await ctx.message.delete(delay=0.5)


@bot.command(aliases=["modify","m"],pass_context=True)
async def _modify(ctx):
    if await checkPerms(ctx):
        return
    if bot.currentitem=="none":
        await ctx.send(embed=getEmbed("В модификаторе нет предмета",discord.Color.dark_orange()),delete_after=10)
        await ctx.message.delete(delay=0.5)
    elif bot.keen==False:
        await ctx.send(embed=getEmbed("В модификаторе нет невежи",discord.Color.dark_orange()),delete_after=10)
        await ctx.message.delete(delay=0.5)
    else:
        gem_chance = 1.0
        if bot.gems_in[0]==True:
            gem_chance+=0.125
        if bot.gems_in[1]==True:
            gem_chance+=0.125
        if bot.gems_in[2]==True:
            gem_chance+=0.125    
        if bot.gems_in[3]==True:
            gem_chance+=0.125
        if bot.tanec==1:
            gem_chance*=2
            bot.tanec=2
        if bot.mix==1:
            gem_chance*=2
            bot.mix=2
        if bot.tfive == 1:
            gem_chance*=1.05
        elif bot.tsix == True:
            gem_chance*=1.25
        if ctx.message.author.premium_since is not None:
            gem_chance*=1.1
        chance = chances[bot.currentmod] * gem_chance
        rnum = random.uniform(0.0,100.0)
        if rnum<chance:
            bot.currentmod+=1
            if bot.tfive == 1:
                bot.tfive = 2
            cit = bot.currentitem
            cmod = bot.currentmod
            cown = bot.currentowner
            cownid = bot.currentownerid
            success()
            if cownid!=ctx.message.author.id:
                await ctx.send(embed=getEmbed("**"+ctx.message.author.name+"** выхватил(а) из рук **"+cown+"** модификатор и заточил(а) "+cit+" на +"+str(cmod)+"!",discord.Color.green()))    
            else:
                await ctx.send(embed=getEmbed("**"+cown+"** заточил(а) "+cit+" на +"+str(cmod)+"!",discord.Color.green()))
            await ctx.message.delete(delay=0.5)
        else:
            fail_ch = 100.0 - chance
            if bot.tfive == 1:
                fail_ch *= 0.75
                bot.tfive = 2
            elif bot.tsix == True:
                fail_ch *= 1
            else:
                fail_ch *= 0.25
            #print("rn: "+str(rnum)+" | ch: "+str(chance)+" | fl: "+str(fail_ch))
            if rnum <= (chance+fail_ch):
                await ctx.send(embed=getEmbed("Неудача, ну хоть оружие не сгорело.",discord.Color.dark_orange()),delete_after=20)
                await ctx.message.delete(delay=0.5)
                neudacha()
            else:
                nogems = ""
                if False in bot.gems_in:
                    nogems = "Возможно с камнями было бы иначе\n"
                cit = bot.currentitem
                cmod = bot.currentmod
                oid = bot.currentownerid
                cown = bot.currentowner
                fail()
                box = sqlutils.addBox(oid,getRandomBox(cmod))                
                if oid!=ctx.message.author.id:
                    await ctx.send(embed=getEmbed("**"+ctx.message.author.name+"** сломал(а) чужой "+cit+" +"+str(cmod)+"\n"+nogems+"**"+cown+"**, вот вам "+boxes[box]+" в качестве утешительного приза",discord.Color.dark_red()))
                else:
                    await ctx.send(embed=getEmbed(cit+" +"+str(cmod)+" сломался\n"+nogems+"**"+cown+"**, вот вам "+boxes[box]+" в качестве утешительного приза",discord.Color.dark_red()))
                await ctx.message.delete(delay=0.5)


@bot.command(pass_context=True)
async def modik(ctx):
    if await checkPerms(ctx):
        return
    if bot.currentitem=="none":
        await ctx.send(embed=getEmbed("В модификаторе нет предмета",discord.Color.dark_orange()),delete_after=10)
        await ctx.message.delete(delay=0.5)
        return
    elif bot.currentmod > 0:
        await ctx.send(embed=getEmbed("Модик можно использовать только с оружием +0",discord.Color.dark_orange()),delete_after=10)
        await ctx.message.delete(delay=0.5)
        return
    if sqlutils.getItemFromInventory(ctx.message.author.id,"modik") == True:
        rnd_num = random.uniform(0.0,100.0)
        if rnd_num<=10:
            bot.currentmod = 4
        elif rnd_num<=35:
            bot.currentmod = 3
        else:
            bot.currentmod = 2
        sqlutils.saveTopToDB(bot.currentitem,bot.currentmod,bot.currentowner,bot.currentownerid)
        sqlutils.saveCurrent(bot.currentitem,bot.currentowner,bot.currentmod)
        await ctx.send(embed=getEmbed("**"+bot.currentowner +"** заточил(а) "+bot.currentitem+" на +"+str(bot.currentmod)+"!",discord.Color.green()))
        await ctx.message.delete(delay=0.5)


@bot.command(pass_context=True)
async def t6(ctx):
    if await checkPerms(ctx):
        return
    if True not in bot.gems_in:
        await ctx.send(embed=getEmbed("В модификаторе нет камней, которые можно было бы заменить",discord.Color.dark_orange()),delete_after=10)
        await ctx.message.delete(delay=0.5)
    elif bot.tfive == 1:
        await ctx.send(embed=getEmbed("Камни Т5 нельзя заменить на камни Т6",discord.Color.dark_orange()),delete_after=10)
        await ctx.message.delete(delay=0.5)
    elif bot.tsix == True:
        await ctx.send(embed=getEmbed("В модификаторе итак уже камни Т6",discord.Color.dark_orange()),delete_after=10)
        await ctx.message.delete(delay=0.5)
    else:
        if sqlutils.getItemFromInventory(ctx.message.author.id,"tsix") == True:
            bot.tsix = True
            await ctx.send(embed=getEmbed("**"+ctx.message.author.name+"** меняет Т4 камни на Т6",discord.Color.purple()),delete_after=10)
            await ctx.message.delete(delay=0.5)
        else:
            await ctx.send(embed=getEmbed("**"+ctx.message.author.name+"**, у вас нет камней Т6",discord.Color.dark_orange()),delete_after=10)
            await ctx.message.delete(delay=0.5)

@bot.command(pass_context=True)
async def inv(ctx):
    if await checkPerms(ctx):
        return
    inventory = sqlutils.getFullInventory(ctx.message.author.id)
    if len(inventory)>0:
        for small,medium,large,tfive,tsix,modik in inventory:
            message = ""
            if small>0:
                message += boxes[0]+": "+str(small)+" шт."
            if medium>0:
                if message!="":
                    message+="\n"
                message += boxes[1]+": "+str(medium)+" шт."
            if large>0:
                if message!="":
                    message+="\n"
                message += boxes[2]+": "+str(large)+" шт."
            if tfive>0:
                if message!="":
                    message+="\n"
                message += gems_complects[0]+": "+str(tfive)+" шт."
            if tsix>0:
                if message!="":
                    message+="\n"
                message += gems_complects[1]+": "+str(tsix)+" шт."
            if modik>0:
                if message!="":
                    message+="\n"
                message += gems_complects[2]+": "+str(modik)+" шт."
            if message!="":
                embed=discord.Embed(title="Содержимое инвентаря **"+ctx.message.author.name+"**:",description=message,color=discord.Color.blue())
                await ctx.send(embed=embed)
                await ctx.message.delete(delay=0.5)
            else:
                await ctx.send(embed=getEmbed("**"+ctx.message.author.name+"**, ваш инвентарь пуст",discord.Color.dark_orange()),delete_after=10)
                await ctx.message.delete(delay=0.5)
    else:
        await ctx.send(embed=getEmbed("**"+ctx.message.author.name+"**, ваш инвентарь пуст",discord.Color.dark_orange()),delete_after=10)
        await ctx.message.delete(delay=0.5)

async def openAll(ctx):
    inventory = sqlutils.getInventory(ctx.message.author.id)
    if len(inventory)>0:
        prem = False
        if ctx.message.author.premium_since is not None:
            prem = True
        maxR = 100.0
        if prem is True:
            maxR -= 25
        for small,medium,large in inventory:
            total = small+medium+large
            if total==0:
                await ctx.send(embed=getEmbed("**"+ctx.message.author.name+"**, ваш инвентарь пуст",discord.Color.dark_orange()),delete_after=10)
                await ctx.message.delete(delay=0.5)
                return
            sqlutils.setBoxesToZero(ctx.message.author.id)
            empty = 0
            tfive = 0
            tsix = 0
            modik = 0
            bumaga = 0
            for x in range(small):
                rnd_num = random.uniform(0.0,maxR)
                if rnd_num<=1:
                    tsix += 1
                elif rnd_num<=2:
                    modik += 1
                elif rnd_num<=3:
                    bumaga += 1
                elif rnd_num<=28:
                    tfive += 1
                else:
                    empty +=1
            for x in range(medium):
                rnd_num = random.uniform(0.0,maxR)
                if rnd_num<=3:
                    tsix += 1
                elif rnd_num<=2:
                    modik += 6
                elif rnd_num<=7:
                    bumaga += 1
                elif rnd_num<=57:
                    tfive += 1
                else:
                    empty +=1
            for x in range(large):
                rnd_num = random.uniform(0.0,maxR)
                if rnd_num<=10:
                    tsix += 1
                elif rnd_num<=20:
                    modik += 1
                elif rnd_num<=21:
                    bumaga += 1
                else:
                    tfive += 1
            message = "**"+ctx.message.author.name+"** открыл(а) все свои коробки ("+str(total)+" шт.) и достал(а):"
            if empty>0:
                message+="\nПустые коробки: "+str(empty)+" шт."
            if bumaga>0:
                message+="\nТуалетная бумага <:bumaga:910831599631888404>: "+str(bumaga)+" шт."
            if tfive>0:
                message+="\nКомплекты Т5 <:tfive:913615358525583432>: "+str(tfive) + " шт."
            if tsix>0:
                message+="\nКомплекты Т6 <:tsix:913615358777233450>: "+str(tsix) + " шт."
            if modik>0:
                message+="\nМодификаторы 2-4 <:modik24:913615095714693222>: "+str(modik) + " шт."
            sqlutils.addItems(tfive,tsix,modik,ctx.message.author.id)
            await ctx.send(embed=getEmbed(message,discord.Color.blue()))
            await ctx.message.delete(delay=0.5)
    else:
        await ctx.send(embed=getEmbed("**"+ctx.message.author.name+"**, ваш инвентарь пуст",discord.Color.dark_orange()),delete_after=10)
        await ctx.message.delete(delay=0.5)

@bot.command(pass_context=True)
async def box(ctx,arg):
    if await checkPerms(ctx):
        return
    if arg=="all":
        await openAll(ctx)
        return
    if arg not in boxes:
        await ctx.send(embed=getEmbed("**"+ctx.message.author.name+"**, этот предмет нельзя открыть",discord.Color.dark_orange()),delete_after=10)
        await ctx.message.delete(delay=0.5)
        return
    box_id = boxes.index(arg)
    inventory = sqlutils.getInventory(ctx.message.author.id)
    if len(inventory)>0:
        prem = False
        if ctx.message.author.premium_since is not None:
            prem = True
        for small,medium,large in inventory:
            result = "-"
            if box_id==0:
                if small>0:
                    result = sqlutils.openBox(ctx.message.author.id,"small",small,prem)  
                else:
                    await ctx.send(embed=getEmbed("**"+ctx.message.author.name+"**, у вас нет маленьких коробок",discord.Color.dark_orange()),delete_after=10)
                    await ctx.message.delete(delay=0.5)
                    return
            elif box_id==1:
                if medium>0:
                    result = sqlutils.openBox(ctx.message.author.id,"medium",medium,prem)
                else:
                    await ctx.send(embed=getEmbed("**"+ctx.message.author.name+"**, у вас нет средних коробок",discord.Color.dark_orange()),delete_after=10)
                    await ctx.message.delete(delay=0.5)
                    return
            elif box_id==2:
                if large>0:
                    result = sqlutils.openBox(ctx.message.author.id,"large",large,prem)
                else:
                    await ctx.send(embed=getEmbed("**"+ctx.message.author.name+"**, у вас нет больших коробок",discord.Color.dark_orange()),delete_after=10)
                    await ctx.message.delete(delay=0.5)
                    return
            if result=="-":
                await ctx.send(embed=getEmbed("**"+ctx.message.author.name+"** открывает коробку, но она оказалась пустой",discord.Color.red()),delete_after=10)
                await ctx.message.delete(delay=0.5)
            else:
                await ctx.send(embed=getEmbed("**"+ctx.message.author.name+"** достал(а) из коробки: "+result,discord.Color.green()))
                await ctx.message.delete(delay=0.5)
    else:
        await ctx.send(embed=getEmbed("**"+ctx.message.author.name+"**, ваш инвентарь пуст",discord.Color.dark_orange()),delete_after=10)
        await ctx.message.delete(delay=0.5)

def getRandomBox(modif):
    maxR = box_chanses[modif]
    if bot.premium is True:
        maxR *= 0.75
    rnum = random.uniform(0.0,maxR)
    if rnum<=1:
        return 2
    elif rnum<=25:
        return 1
    else:
        return 0

@bot.command(pass_context=True)
async def status(ctx):  
    if await checkPerms(ctx):
        return
    if bot.currentitem=='none':
        await ctx.send(embed=getEmbed("В модификаторе нет предмета",discord.Color.dark_orange()),delete_after=10)
        await ctx.message.delete(delay=0.5)
    else:
        await ctx.send(embed=getEmbed("В модификаторе сейчас "+bot.currentitem+" +"+str(bot.currentmod)+" (Владелец: **"+bot.currentowner+"**)",discord.Color.magenta()))
        await ctx.message.delete(delay=0.5)

def success():
    sqlutils.saveTopToDB(bot.currentitem,bot.currentmod,bot.currentowner,bot.currentownerid)
    if bot.currentmod==7:
        sqlutils.saveCurrent('none','-',0)
        sqlutils.saveCd(bot.currentownerid,bot.premium)
    else:
        sqlutils.saveCurrent(bot.currentitem,bot.currentowner,bot.currentmod)
    bot.keen = False
    bot.gems_in[0] = False
    bot.gems_in[1] = False
    bot.gems_in[2] = False
    bot.gems_in[3] = False
    bot.tsix = False
    if bot.currentmod==7:
        bot.currentitem='none'
        bot.currentowner = '-'
        bot.currentownerid = '0'
        bot.currentmod = 0
        bot.tanec = 0
        bot.tfige = 0
        bot.mix = 0

def fail():
    sqlutils.saveCurrent('none','-',0)
    premium = False
    
    sqlutils.saveCd(bot.currentownerid,bot.premium)
    bot.keen = False
    bot.gems_in[0] = False
    bot.gems_in[1] = False
    bot.gems_in[2] = False
    bot.gems_in[3] = False
    bot.tanec = 0
    bot.tfive = 0
    bot.tsix = False
    bot.mix = 0
    bot.currentitem='none'
    bot.currentowner='-'
    bot.currentownerid = '0'
    bot.currentmod = 0

def neudacha():
    bot.keen = False
    bot.gems_in[0] = False
    bot.gems_in[1] = False
    bot.gems_in[2] = False
    bot.gems_in[3] = False
    bot.tsix = False

def sortBy(e):
  return e['mod']


@bot.command(pass_context=True)
async def test(ctx,arg):
    print(arg)


@bot.command(pass_context=True)
async def top(ctx):
    if waitForCommand():
        await ctx.message.delete(delay=0.5)
        return
    #if ctx.channel.id !=allowed_id:
    #    await ctx.send(content=ctx.message.author.mention+" кыш, в этом канале нельзя пользоваться ботом!",delete_after=20)
    #    await ctx.message.delete(delay=0.5)
    #    return
    topList = sqlutils.getTop()
    maxVal = len(topList)
    if maxVal>10:
        maxVal = 10
    index = 0
    message = ""
    for id, name, item, modif, amount in topList:
        if index<10:
            message += str(index+1)+". "+name+": "+item+" +"+str(modif)+" ("+str(amount)+")"
            if index < maxVal-1:
                message+="\n"
        elif id==str(ctx.message.author.id):
            if index>0:
                message+="\n..." 
            message+="\n"+str(index+1)+". "+name+": "+item+" +"+str(modif)+" ("+str(amount)+")"
        index+=1
    await ctx.send(embed=getEmbed(message,discord.Color.blue()))
    await ctx.message.delete(delay=0.5)

def loadFile():
    current = sqlutils.getCurrent()
    for item, owner, modif, owid in current:
        bot.currentitem = str(item)
        bot.currentmod = int(modif)
        bot.currentowner = str(owner)
        bot.currentownerid = int(owid)

loadFile()

def gems_ok(arg):
    args = arg.split('-')
    if len(args)!=4 or args[0] not in gems or args[1] not in gems or args[2] not in gems or args[3] not in gems:
        return False
    else: 
        return True

async def on_error(ctx,ex):
    comm = str(ctx.message.content)
    ctx.delete_after = 5
    if 'item' in comm or 'gem' in comm or 'talika' in comm:
        await ctx.send(embed=getEmbed("Что-то пошло не так, возможно вы забыли пробел",discord.Color.dark_orange()))
    else:
        await ctx.send(embed=getEmbed("Такой команды не существует",discord.Color.dark_orange()))

#bot.add_listener(on_error,'on_command_error')
bot.run(TOKEN)



