import subprocess
import re
from datetime import datetime
from datetime import timedelta


def menu():
    print('Check balance - 1')
    print('Leader Slots  - 2')
    print('Epoch info    - 3')
    print('Vote info     - 4')
    print('Validators    - 5')


def get_vote(identity_list):
    vote_list = []
    for i in range(len(identity_list)):
        vt = subprocess.check_output('solana validators | grep ' + identity_list[i] + ' | awk \'{print $3}\'',
                                     shell=True, universal_newlines=True)
        vote_list.append(vt[:-1])
    return vote_list


def end_of_epoch():
    full_info = subprocess.check_output('solana epoch-info', universal_newlines=True, shell=True)
    parent = re.findall(r"\((.*?)\)", full_info)  # list of texts in parentheses

    d = re.findall(r"\d+d", parent[-1])  # days to end of epoch
    if not d:
        d.append('0d')

    h = re.findall(r"\d+h", parent[-1])  # hours to end of epoch
    if not h:
        h.append('0h')

    m = re.findall(r"\d+m", parent[-1])  # minutes to end of epoch
    if not m:
        m.append('0m')

    s = re.findall(r"\d+s", parent[-1])  # seconds to end of epoch
    if not s:
        s.append('0s')

    now = datetime.now()
    eoe = now + timedelta(days=int(d[-1][:-1]), hours=int(h[-1][:-1]),
                          minutes=int(m[-1][:-1]) + round(int(s[-1][:-1]) / 60))

    print('*' * 50 + '\nCurrent time:        ', str(now)[:-10])
    print('Approx. end of epoch:', str(eoe)[:-10])
    print('*' * 50 + '\n')


def check_balance(identity_list, vote_list):
    for i in range(len(identity_list)):
        bal1 = subprocess.check_output('solana balance ' + identity_list[i], universal_newlines=True, shell=True)
        bal2 = subprocess.check_output('solana balance ' + vote_list[i], universal_newlines=True,
                                       shell=True)
        print('Identity (' + identity_list[i][:5] + '):\t' + bal1, end='')
        print('Vote (' + vote_list[i][:5] + '):\t\t' + bal2)


def leader_slots(identity_list):
    for i in range(len(identity_list)):
        validator_info = subprocess.check_output('solana validators | grep ' + identity_list[i],
                                                 universal_newlines=True, shell=True)
        total = subprocess.check_output('solana leader-schedule | grep ' + identity_list[i] + ' | wc -l',
                                        universal_newlines=True, shell=True)
        # Added for validators with no "Completed Leader Slots" by now
        try:
            leader_slots_info = subprocess.check_output('solana block-production | grep ' + identity_list[i],
                                                        universal_newlines=True, shell=True)
        except subprocess.CalledProcessError:
            leader_slots_info = '0' * 81

        credits = int(validator_info[143:150])
        blocks_produced = int(leader_slots_info[75:82])
        commission = credits * 5e-6 - blocks_produced * 375e-5
        print(identity_list[i][:5])
        print(
            'Total leader slots   Completed Leader Slots  Blocks Produced    Skipped Slots  Skipped Slot Percentage   '
            'Commission')
        if leader_slots_info[0] != '0':
            print(total[:-1].rjust(18) + ' ' * 12 + leader_slots_info[50:-1] + '◎{0:.3f}'.format(commission).rjust(
                13) + '\n')
        else:
            print(total[:-1].rjust(18) + ' ' * 84 + '◎{0:.3f}'.format(commission).rjust(13) + '\n')


def validators(identity_list):
    ids = ''
    for i in identity_list:
        ids = ids + ' -e ' + i
    subprocess.Popen('solana validators --sort=credits -r -n | sed -n 1,2p && solana validators --sort=credits -r -n '
                     '| grep' + ids, shell=True).wait()


##########################################################################################################
identity = ['A1enabzLW77R2VVg67CLv3kNJ5FWVnAmC6pKcZwCmkXB', 'sh4rkGLyKwi8q1n8bwYkDiUC2n1cs6tbWSTGogd45d6']
vote = get_vote(identity)

menu()

while True:
    cmd = input('\nChoose option: ')
    if cmd == '1':
        print('*** Balances ***')
        check_balance(identity, vote)
    elif cmd == '2':
        print('*** Leader slots ***')
        leader_slots(identity)
    elif cmd == '3':
        print('*** Epoch Info ***')
        subprocess.Popen('solana epoch-info', shell=True).wait()
        end_of_epoch()
    elif cmd == '4':
        print('*** Vote Info with Rewards ***')
        for key in vote:
            while True:
                n = input('How many reward epochs to show for vote [' + key + ']? Enter number between 1 and 5: ')
                if n in ['1', '2', '3', '4', '5']:
                    break
                else:
                    print('Try again...')
            subprocess.Popen('solana vote-account ' + key + ' --with-rewards --num-rewards-epochs ' + n,
                             shell=True).wait()
        menu()
    elif cmd == '5':
        print('*** Validators info ***')
        validators(identity)
    else:
        break
