#!/usr/bin/env python
# simple app
from rtm import createRTM, RTM
import logging
from string import Template

API_KEY="8db21291ccdbcd858059799cb44dc57c"
API_SEC="5d80e818ec7aa0b4"

API_TOK="abee05a338c1799fe8f86bde83de573e9628cfe7"

TZ_DEFAULT=84 # Chicago CDT


def setupSchool(rtm):
    plist=""".d.General
    .d.FileStruct
    .d.LatinAmer
    .d.TechWrit
    .d.GUID
    .d.ISAnalysis
    .d.MktPrin
    """
    projects = map(str.strip, plist.split("\n"))
    print projects

    for p in projects:
        addTask(rtm,"Add Assignments to RTM",tags=['-next','@online',p],estimate='15 minutes')


def examp(rtm):
    return [(x.id, x.name,x.tags and x.tags.tag or []) for x in rtm.tasks.getList(filter='list:Inbox').tasks.list.taskseries]


class RMilk(RTM):
    def __init__(self,apiKey=API_KEY,secret=API_SEC,token=API_TOK):
        # TODO: Proper subclass (ie no monkeypatch)
        super(RMilk,self).__init__(apiKey,secret,token)
        
        if 0 and token is None:
            print 'No token found'
            print 'Login here:', rtm.getAuthURL()
            raw_input('Press enter after logging in at the link above')
            token = rtm.getToken()
            print 'Remember this token:', token
            super(RMilk,self).__init__(self,apiKey,secret,token)

        self._tl = self.timelines.current = self.timelines.create().timeline

        #rtm.LISTS = getListDict()
        self.LISTS = {u'Daily': u'4574767', u'Inbox': u'3917063', u'Sent': u'3917067'}


def addTask(rtm, name, tags=None,
        due_date=None, estimate=None, repeat=None,
        priority=None, parse=True, atomic=True):
    '''Wrapper for task add.
    List defaults to Inbox
    Set atomic to false if handling batches
    '''

    if not name:
        logging.error("A task must have a name")
        raise Exception

    if atomic:
        rtm._tl = rtm.timelines.create().timeline

    try:
        tr = rtm.tasks.add(timeline=rtm._tl,name=name,parse=parse)
        list_id = tr.list.id
        tser_id = tr.list.taskseries.id
        task_id = tr.list.taskseries.task.id
        logging.debug(':'.join([list_id, tser_id, task_id]))

        if tags:
            rtm.tasks.addTags(timeline=rtm._tl, list_id=list_id,
                    taskseries_id=tser_id, task_id=task_id,
                    tags=','.join(tags))
        if due_date:
            rtm.tasks.setDueDate(timeline=rtm._tl, list_id=list_id,
                    taskseries_id=tser_id, task_id=task_id,
                    due=due_date, parse=1)
        if estimate:
            rtm.tasks.setEstimate(timeline=rtm._tl, list_id=list_id,
                    taskseries_id=tser_id, task_id=task_id,
                    estimate=estimate)
        if repeat:
            rtm.tasks.setRecurrance(timeline=rtm._tl, list_id=list_id,
                    taskseries_id=tser_id, task_id=task_id,
                    repeat=repeat)
        if priority:
            rtm.tasks.setPriority(timeline=rtm._tl, list_id=list_id,
                    taskseries_id=tser_id, task_id=task_id,
                    priority=priority)

        if settags:
            rtm.tasks.setTags(timeline=rtm._tl, list_id=list_id,
                    taskseries_id=tser_id, task_id=task_id,
                    tags=','.join(settags))

    except:
        logging.error("Problem with adding a task")
        # TODO: Handle transactions correctly

    return (list_id, task_id, tser_id)


def test_addTask(rtm=RMilk()):
    addTask(rtm,"wow",tags=['pretty','cool'],parse=False)


def getTimezones(rtm=RMilk()):
    print '\n'.join([' : '.join(
        [x.name, x.id, x.dst, x.offset, x.current_offset])
        for x in tz.timezones.timezone if 'America' in x.name])

def getListDict(rtm=RMilk()):
    r = rtm.lists.getList()
    return dict(map(lambda x:(x.name, x.id), filter(lambda x: x.smart == u'0', r.lists.list)))

def getList(rtm=RMilk(), list_id=None, filter=''):
    rtm.tasks.getList(list_id, filter=filter)

    # cast return structure to task

TEMPLATE_TASK = \
        Template(
                '''Name: ${name}
Tags: ${tags}
Due : ${due_date}
Est : ${estimate}
Pri : ${priority}''')

class Task(object):
    def __init__(self, name, tags=None, due_date=None, estimate=None,
            repeat=None, priority=None, parse=None,
            id=None, list_id=None):
        self.name=name
        self.tags=tags
        self.due_date=due_date
        self.estimate=estimate
        self.repeat=repeat
        self.priority=priority
        self.parse=parse
        self.id=id
        self.list_id=list_id
        #self.list_name

    def save(self, rtm):
        try:
            (self.list_id, self.id, self.tser_id) = \
                    addTask(rtm, self.name, self.tags, self.due_date,
                            self.estimate,self.repeat, self.priority, True, True)
                    # update self with relevant
            logging.info("Saved task: %s (%s:%s)" % \
                    (self.name, self.list_id, self.id))
            return True
        except:
            logging.error("Error saving task")
            return False


    def __str__(self):
        return TEMPLATE_TASK.substitute({
            'name':self.name,
            'tags':self.tags and ', '.join(self.tags) or '',
            'due_date': self.due_date or '',
            'estimate': self.estimate or '',
            'priority': self.priority or ''})

        def __str_detailed__(self):
            print str(self)
            print 'id  :', self.id
            print 'lid :', self.list_id
            print 'tser:', self.tser_id


def test_Task(rtm=RMilk()):
    t = Task("wow",tags=['prety','@cool'], due_date="tomorrow", estimate="10 minutes")
    t.save(rtm)
    print t.__str_detailed__()
    assert t.id is not None
    assert t.list_id is not None


if __name__=="__main__":
    #    print '\n'.join(map(str,examp(RMilk())))
    from optparse import OptionParser
    from operator import xor
    arg = OptionParser(version="%prog 0.1")

    arg.add_option('-c','--create',dest='create', action='store_true',
            help='Create a new task')
    arg.add_option('-n','--name',dest='name',help='Task name')
    arg.add_option('-t','--tags',dest='tags', help='Task tags (comma separated)')
    arg.add_option('-d','--due',dest='due_date', help='Due date')
    arg.add_option('-e','--estimate',dest='estimate', help='Task time estimate')
    arg.add_option('-r','--repeat',dest='repeat',help='Task repetition')
    arg.add_option('-p','--priority',dest='priority',help='Task priority')
    arg.add_option('-l','--list',dest='get_list',help='Get list by filter')

    arg.add_options('--rename',dest='tag_rename',nargs=2,help='Rename <original> with <tag>. Requires list filter')
    arg.add_option('--test',dest='test',action='store_true',help='Testing')

    (options, args) = arg.parse_args()

    actions={'-c/--create':options.create,
            '-l/--list':options.get_list,
            '--test':options.test}

    # Exclusive actions
    if not reduce(xor, map(bool, actions.values())):
        logging.error("Can only select one of %s" % ', '.join(actions.keys()))
        exit()

    if options.test:
        rtm = RMilk()
        test_Task(rtm)
        exit()

    # Normalize tags list
    if options.tags:
        options.tags = map(str.strip, options.tags.split(','))

    if options.create:
        t = Task(options.name, options.tags, options.due_date,
                options.estimate, options.repeat, options.priority,
                parse=True)
        t.save(RMilk())

    if options.get_list:
        print "list by formatter selection"

    if options.tag_rename: # 2 options
        # get list by filter
        #for task in casted_to_task_tasklist:
            #settags(current_tags - original + newtag
            #print task
        (old,new) = options.tag_rename
        print "%s --> %s" % (old,new)


#[(x.name, x.tags.tag or []) for x in r.tasks.getList(filter="tagContains:.is").tasks.list[1].taskseries]
