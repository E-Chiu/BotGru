import discord # for...discord.py
import importantFile # file with important stuff ;)
import sqlite3 # for database
import asyncio # for catching that one specific error
import uuid # for random id generation
import datetime # for getting date and time
import random # for random
import os # to have access to directory

# TODO
# add option to set time for digest
# have time for calendar events, ping them when its time
# have option to ping user after patch notes (and also disable the option)
# make sure you must be registered before doing anything
# figure out that color card thing bots can send and use 
# add option for me to send global message


client = discord.Client() # start discord client
random.seed() # seed random
months = ["January", "Febuary", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
pre = '~' #prefix to use for commands
filename = '%s/botgru.db' % os.getcwd()

@client.event
async def on_ready(): # called when bot is ready to be used
    client.loop.create_task(check_reminders()) # start loop to check for notis
    await client.change_presence(activity=discord.Game(name = "Try [~help]!"))
    print('Logged in as:')
    print(client.user.name)

@client.event
async def on_message(message):
    Conn = sqlite3.connect(filename) # open database
    c = Conn.cursor() # make cursor for db
    userID = message.author.id # id of who sent message

    if message.author == client.user: # if the message is sent from the bot do nothing
        return

    if message.content.startswith('-test'):
        await message.channel.send('`Bot is working`')

    if message.content.startswith(pre + 'help'):
        helpCommand = message.content[6:]
        if helpCommand == '': # if no following text show general help
            # its gonna look scuffed but discord wants me to have one long line :)
            await message.channel.send("----------HELP----------\nTo get additional description, type`" + pre + "help " + pre + "[command]`\n`" + pre + "cal`: Personal calendar you can add events to and will remind you\n`" + pre + "note`: Save text or have a timed message be sent to you\n`" + pre + "gru`: Gru\n`" + pre + "settings`: set user settings\n`" + pre + "patch`: see patch notes\n`" + pre + "register`: register yourself first time you add the bot")
        elif helpCommand == pre + "cal":
            await message.channel.send("----------CAL----------\n`" + pre + "cal show cal [yyyy]-[mm]`: Show your current calendar for yyyy year, mm month. To show all do `" + pre + "cal show 0000-00`\n`" + pre + "cal add [name]`: Start a new event to your calendar\n`" + pre + "cal del [ID]`: Remove an event from your calendar\n`" + pre + "cal edit [ID]`: Change something about an event\n`" + pre + "cal clear [yyyy]-[mm]`: Clear the whole calandar for yyyy year, mm month")
        elif helpCommand == pre + "note":
            await message.channel.send("----------NOTE----------\n`" + pre + "note show`: Show all your current notes\n`" + pre + "note add [note]`: Add a note to your notebook\n`" + pre + "note reminder [timer (minutes)]; [note]`: Add a timed reminder to your notebook\n`" + pre + "note del [ID]`: delete a note from your notebook\n`" + pre + "note clear`: delete all your notes")
        elif helpCommand == pre + "register":
            await message.channel.send("----------REGISTER----------\n`" +pre + "register`: type this to register yourself the first time you use this bot")
        elif helpCommand == pre + "gru":
            await message.channel.send("Gru")
        elif helpCommand == pre + "settings":
            await message.channel.send("----------SETTINGS----------\n`" + pre + "settings digest (n,d[x],w,m)`: set how frequent you get digests (none, days, week, month)\n`" + pre + "report [feedback]`: submit a report that gets dmed to maker")
        elif helpCommand == pre + "patch":
            await message.channel.send("`VER 1.01`: Basic functionality added. Started spamming people to test it with me :)")

        if message.content.startswith(pre + 'cal'):
            if message.content.startswith(pre + "cal show"): # show events for month if exists
                try:
                    yearMonthS = message.content[10:18] + "-00" # month user wants
                    yearMonthE = yearMonthS[0:5] + str(int(yearMonthS[5:7]) + 1).zfill(2) + yearMonthS[7:10] # start of next month
                    if yearMonthS == '0000-00-00': # show all
                        c.execute('''
                        SELECT eid, date, title, desc FROM events
                        WHERE user_id = ?
                        order by date;
                        ''', (userID,))
                        rows = c.fetchall()
                        if len(rows) == 0:
                            await message.channel.send("You have no calendar events, try adding some!")
                        else: # print out the query
                            await message.channel.send("|---ID---|-----DATE-----|-----TITLE-----|------DESC------|")
                            for i in range(len(rows)):
                                eventRow = '' # loop through and concatenate a string
                                for j in range(len(rows[i])):
                                    eventRow = eventRow + '| ' + rows[i][j] + ' '
                                eventRow = eventRow + '|'
                                await message.channel.send(eventRow)
                    else:
                        # verify that input was a legitimate date
                        # but too lazy to make sure day works with the correct month
                        if 0 < int(yearMonthS[0:4]) and 1 <= int(yearMonthS[5:7]) <= 12 and yearMonthS[4] == '-' and yearMonthS[7] == '-':
                            c.execute('''
                            SELECT eid, date, title, desc FROM events
                            WHERE user_id = ? AND date between ? and ?
                            order by date;
                            ''', (userID, yearMonthS, yearMonthE,))
                            rows = c.fetchall()
                            if len(rows) == 0:
                                await message.channel.send("You have no calendar events for " + months[int(yearMonthS[5:7]) - 1] + ", try adding some!")
                            else: # print out the query
                                await message.channel.send("|---ID---|-----DATE-----|-----TITLE-----|------DESC------|")
                                for i in range(len(rows)):
                                    eventRow = '' # loop through and concatenate a string
                                    for j in range(len(rows[i])):
                                        eventRow = eventRow + '| ' + rows[i][j] + ' '
                                    eventRow = eventRow + '|'
                                    await message.channel.send(eventRow)
                        else:
                            raise
                except:
                    await message.channel.send("Hmm, looks like some input was wrong")
            elif message.content.startswith(pre + "cal add"): # add new event
                eventTitle = message.content[8:]
                await message.channel.send("Would you like to add a event description? (Y/N)")
                try:
                    descBool = (await client.wait_for("message", timeout = 30)).content
                    eventDesc = ''
                    if descBool.lower() == 'y': # get event description if they want to add
                        await message.channel.send("What is the description for " + eventTitle +" ?")
                        try:
                            eventDesc = descBool = (await client.wait_for("message", timeout = 120)).content
                        except asyncio.TimeoutError:
                            await message.channel.send("Whoops, took too long!")
                    await message.channel.send("Enter a date for the event [yyyy]-[mm]-[dd]")
                    try: # get date and make event
                        eventDate = (await client.wait_for("message", timeout=60)).content      
                        # verify that input was a legitimate date
                        # but too lazy to make sure day works with the correct month
                        if 0 < int(eventDate[0:4]) and 1 <= int(eventDate[5:7]) <= 12 and 1 <= int(eventDate[8:10]) <= 31 and eventDate[4] == '-' and eventDate[7] == '-':
                            eid = str(uuid.uuid4())[:5] # get 5 digit unique id
                            # add event to db
                            c.execute('''
                            INSERT INTO events VALUES
                            (?,?,?,?,?);
                            ''',(eid,eventTitle,eventDesc,eventDate,userID,))
                            await message.channel.send("New event has been created!")
                        else:
                            raise
                    except asyncio.TimeoutError:
                        await message.channel.send("Whoops, took too long!")
                    except:
                        await message.channel.send("Hmm, looks like some input was wrong")
                except asyncio.TimeoutError:
                    await message.channel.send("Whoops, took too long!")
            elif message.content.startswith(pre + "cal del"): # delete an event
                eventID = message.content[9:]
                # delete if eid and uid match
                c.execute('''
                    DELETE FROM events
                    WHERE eid = ? and user_id = ?;
                ''', (eventID,userID,))
                if c.rowcount > 0:
                    await message.channel.send("Event deleted!")
                else:
                    await message.channel.send("Hmm, there is no event under that ID")
            elif message.content.startswith(pre + "cal edit"): # change the atrribute of an event
                eventID = message.content[10:]
                #check if uid and eid match
                c.execute('''
                    SELECT * FROM events
                    WHERE eid = ? and user_id = ?;
                ''', (eventID, userID,))
                if len(c.fetchall()) == 1:
                    await message.channel.send("What do you want to change? (title, date, desc)")
                    try:
                        toChange = (await client.wait_for("message", timeout=30)).content.lower()
                        if toChange == 'title':
                            await message.channel.send("What is the new title?")
                            newTitle = (await client.wait_for("message", timeout=30)).content
                            c.execute('''
                                UPDATE events
                                SET title = ?
                                WHERE eid = ?;
                            ''', (newTitle, eventID,))
                            await message.channel.send("New title set!")
                        elif toChange == 'date':
                            await message.channel.send("What is the new date? ([yyyy]-[mm]-[dd])")
                            newDate = (await client.wait_for("message", timeout=30)).content
                            if 0 < int(newDate[0:4]) and 1 <= int(newDate[5:7]) <= 12 and 1 <= int(newDate[8:10]) <= 31 and newDate[4] == '-' and newDate[7] == '-':
                                c.execute('''
                                    UPDATE events
                                    SET date = ?
                                    WHERE eid = ?;
                                ''', (newDate, eventID,))
                                await message.channel.send("New date set!")
                            else:
                                raise
                        elif toChange == 'desc':
                            await message.channel.send("What is the new description?")
                            newDesc = (await client.wait_for("message", timeout=120)).content
                            c.execute('''
                                UPDATE events
                                SET desc = ?
                                WHERE eid = ?;
                            ''', (newDesc, eventID,))
                            await message.channel.send("New description set!")
                        else:
                            await message.channel.send("Hmm, looks like some input was wrong")
                    except asyncio.TimeoutError:
                        await message.channel.send("Whoops, took too long!")
                    except:
                        await message.channel.send("Hmm, looks like some input was wrong")
                else:
                    await message.channel.send("Hmm, you don't have a note with that id")
            elif message.content.startswith(pre + "cal clear"): # clear all the events within a given month
                try:
                    yearMonthS = message.content[11:19] + "-00" # month user wants
                    yearMonthE = yearMonthS[0:5] + str(int(yearMonthS[5:7]) + 1).zfill(2) + yearMonthS[7:10] # start of next month
                    if 0 < int(yearMonthS[0:4]) and 1 <= int(yearMonthS[5:7]) <= 12 and yearMonthS[4] == '-' and yearMonthS[7] == '-':
                        c.execute('''
                            DELETE FROM events
                            WHERE user_id = ? AND date between ? AND ?
                        ''', (userID, yearMonthS, yearMonthE,))
                    else:
                        raise
                    if c.rowcount > 0:
                        await message.channel.send("Events Deleted!")
                    else:
                        await message.channel.send("There were no events for this month")
                except:
                    await message.channel.send("Hmm, looks like some input was wrong")

        if message.content.startswith(pre + 'note'):
            if message.content.startswith(pre + 'note show'): # show all current notes
                c.execute('''
                    SELECT nid, note FROM notes;
                ''')
                rows = c.fetchall()
                if len(rows) == 0:
                    await message.channel.send("You have no notes, try adding some!")
                else:
                    await message.channel.send("|---ID---|----------NOTE----------|")
                    for i in range(len(rows)):
                        eventRow = ''
                        for j in range(len(rows[i])):
                            eventRow = eventRow + '| ' + rows[i][j] + ' '
                        await message.channel.send(eventRow)
            elif message.content.startswith(pre + "note add"):
                toNote = message.content[9:] # get the note to add
                nid = str(uuid.uuid4())[:5] # get unique uid
                c.execute('''
                    INSERT INTO notes VALUES
                    (?, ?, ?, -1, ?)
                ''', (nid, toNote, str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M")), userID,))
                await message.channel.send("Note has been added!")
            elif message.content.startswith(pre + "note reminder"):
                toNote = message.content[15:]
                toNoteArr = toNote.split(';') # get time and note from string
                nid = str(uuid.uuid4())[:5] # get unique uid
                c.execute('''
                    INSERT INTO notes VALUES
                    (?, ?, ?, ?, ?)
                ''', (nid, toNoteArr[1], str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M")), (datetime.datetime.now() + datetime.timedelta(minutes=int(toNoteArr[0]))).strftime("%Y-%m-%d %H:%M"), userID,))
                await message.channel.send("Note has been added!")
            elif message.content.startswith(pre + 'note del'):
                noteID = message.content[10:]
                # delete if nid and uid match
                c.execute('''
                    DELETE FROM notes
                    WHERE nid = ? and user_id = ?;
                ''', (noteID,userID,))
                if c.rowcount > 0:
                    await message.channel.send("Note deleted!")
                else:
                    await message.channel.send("Hmm, there is no note under that ID")
            elif message.content.startswith(pre + 'note clear'):
                # delete all notes
                c.execute('''
                    DELETE FROM notes
                    where user_id = ?;
                ''', (userID,))
                if c.rowcount > 0:
                    await message.channel.send("Notes cleared!")
                else:
                    await message.channel.send("Hmm, you don't have any notes")
                
        if message.content.startswith(pre + 'register'): # use user id to add to user table
            await message.channel.send("Give yourself a nickname: ")
            try:
                name = (await client.wait_for("message", timeout=30)).content
                # insert uid with nickname into table
                c.execute('''
                    INSERT OR replace INTO users VALUES
                    (?,?,?,?);
                ''', (userID, name, 'n', '-1'))
                await message.channel.send("You have been registered!")
            except asyncio.TimeoutError:
                await message.channel.send("Whoops, took too long!")

        if message.content.startswith(pre + 'gru'): # gru
            gruImg = "./grus/" + random.choice(os.listdir("./grus"))
            await message.channel.send(file=discord.File(gruImg))

        if message.content.startswith(pre + 'settings'):
            if message.content.startswith(pre + 'settings digest'):
                digestSet = message.content[17:18].lower()
                if digestSet in ['n','d','w','m']: # validate input
                    if digestSet == 'd':
                        nextDigest = (datetime.datetime.now() + datetime.timedelta(days=1)).strftime("%Y-%m-%d") + " 02:00"
                    elif digestSet == 'w':
                        nextDigest = (datetime.datetime.now() + datetime.timedelta(weeks=1)).strftime("%Y-%m-%d") + " 02:00"
                    elif digestSet == 'm':
                        nextDigest = (datetime.datetime.now() + datetime.timedelta(months=1)).strftime("%Y-%m") + "-00 02:00"
                    else:
                        nextDigest = '-1'
                    c.execute('''
                        UPDATE users
                        SET digestType = ?,
                        nextDigest = ?
                        WHERE uid = ?
                    ''', (digestSet, nextDigest, userID,))
                    await message.channel.send("Digest settings changed!")
                else:
                    await message.channel.send("Hmm, looks like some input was wrong")
            elif message.content.startswith(pre + 'settings report'):
                feedback = message.content[16:]
                user = await client.fetch_user(importantFile.adminID)
                feedbacker = await client.fetch_user(message.author.id)
                await user.send("FEEDBACK FROM " + feedbacker.name + ":" + feedback)
                await message.channel.send("Feedback sent. Thanks for your help!")

        Conn.commit() # commit any db changes
        Conn.close() # close db

@client.event
async def check_reminders():
    await client.wait_until_ready()
    while True:
        Conn = sqlite3.connect(filename) # open database
        c = Conn.cursor() # make cursor for db
        await client.wait_until_ready()
        timeCurr = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        # see if there are any notes within this time
        c.execute('''
            SELECT user_id, note, nid FROM notes
            WHERE timer = ?;
        ''', (str(timeCurr),))
        rows = c.fetchall()
        # dm users about note
        if len(rows) > 0:
            for i in range(len(rows)):
                user = await client.fetch_user(rows[i][0]) # get user
                await user.send("Reminder:" + rows[i][1] + ". Hope you didn't forget!") # dm user
                # remove the note from the db
                c.execute('''
                    DELETE FROM notes
                    WHERE nid = ?;
                ''', (rows[i][2],))
        # see if there are any digests within this time
        c.execute('''
            SELECT uid, digestType, nextDigest, name FROM users
            WHERE nextDigest = ?
        ''', (timeCurr,))
        rows = c.fetchall()
        # dm users about event
        if len(rows) > 0:
            for i in range(len(rows)):
                # see what type of digest to give
                digestType = (rows[i][1])[0]
                user = await client.fetch_user(rows[i][0]) # get user
                if digestType != 'n': # if some kind of digest is wanted
                    if digestType == 'd': # if day get all digests for today
                        c.execute('''
                            SELECT eid, title FROM events
                            WHERE user_id = ? AND date = ?;
                        ''', (rows[i][0], datetime.datetime.now().strftime("%Y-%m-%d %H:%M")))
                        events = c.fetchall()
                        freq = ['today', 'day'] # for printing digest
                        # set the next date for digest
                        c.execute('''
                            UPDATE users
                            SET nextDigest = ?
                            WHERE uid = ?;
                        ''', ((datetime.datetime.now() + datetime.timedelta(days=1)).strftime("%Y-%m-%d %H:%M"), rows[i][0],))
                    elif digestType == 'w':
                        # get all digests for the week
                        c.execute('''
                            SELECT eid, title FROM events
                            WHERE user_id = ? AND date between ? and ?;
                        ''', (rows[i][0], (datetime.datetime.now() + datetime.timedelta(days=-1)).strftime("%Y-%m-%d %H:%M"), (datetime.datetime.now() + datetime.timedelta(days=1)).strftime("%Y-%m-%d"),))
                        events = c.fetchall()
                        freq = ['this week', 'week']
                        # set the next date for digest
                        c.execute('''
                            UPDATE users
                            SET nextDigest = ?
                            WHERE uid = ?;
                        ''', ((datetime.datetime.now() + datetime.timedelta(weeks=1)).strftime("%Y-%m-%d %H:%M"), rows[i][0],))
                    elif digestType == 'm':
                        # get all digest for the month
                        c.execute('''
                            SELECT eid, title FROM events
                            WHERE user_id = ? AND date between ? and ?;
                        ''', (rows[i][0], (datetime.datetime.now() + datetime.timedelta(days=-1)).strftime("%Y-%m-%d %H:%M"), (datetime.datetime.now() + datetime.timedelta(months=1)).strftime("%Y-%m-%d"),))
                        events = c.fetchall()
                        freq = ['this month', 'month']
                        c.execute('''
                            UPDATE users
                            SET nextDigest = ?
                            WHERE uid = ?;
                        ''', ((datetime.datetime.now() + datetime.timedelta(months=1)).strftime("%Y-%m-%d %H:%M"), rows[i][0],))
                    # print digest or lack thereof
                    if len(events) == 0:    
                        await user.send("Hello" + rows[i][3] + "! Today is " + timeCurr + ". You have no events " + freq[0] + ", have a good " + freq[1] + "!")
                    else:
                        await user.send("Hello" + rows[i][3] + "! Today is " + timeCurr + ". You have the following events " + freq[0] + ":")
                        for i in range(len(events)):
                            await user.send(events[i][1])
                        await user.send("Don't forget to use" + pre + "cal show if you need details. Have a good " + freq[1] + "!")
        Conn.commit() # commit to db
        Conn.close() # close db
        await asyncio.sleep(1) # repeat this every second

client.run(importantFile.token)
