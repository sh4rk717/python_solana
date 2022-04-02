import subprocess
import re
from datetime import datetime
from datetime import timedelta


def end_of_epoch():
    fullinfo = subprocess.check_output('solana epoch-info', universal_newlines=True, shell=True)
    parent = re.findall(r"\((.*?)\)", fullinfo)  # list of texts in parentheses

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
    for key in range(len(identity_list)):
        bal1 = subprocess.check_output('solana balance ' + identity_list[key], universal_newlines=True, shell=True)
        bal2 = subprocess.check_output('solana balance ' + vote_list[key], universal_newlines=True,
                                       shell=True)
        print('Identity (' + identity_list[key][:5] + '):\t' + bal1, end='')
        print('Vote (' + vote_list[key][:5] + '):\t\t' + bal2)


def leader_slots(identity_list):
    for key in range(len(identity_list)):
        validator_info = subprocess.check_output('solana validators | grep ' + identity_list[key],
                                                 universal_newlines=True, shell=True)
        total = subprocess.check_output('solana leader-schedule | grep ' + identity_list[key] + ' | wc -l',
                                        universal_newlines=True, shell=True)
        leader_slots_info = subprocess.check_output('solana block-production | grep ' + identity_list[key],
                                                    universal_newlines=True, shell=True)
        credits = int(validator_info[143:150])
        blocks_produced = int(leader_slots_info[75:82])
        commission = credits * 5e-6 - blocks_produced * 375e-5
        print(identity_list[key][:5])
        print(
            'Total leader slots   Completed Leader Slots  Blocks Produced    Skipped Slots  Skipped Slot Percentage   Commission')
        print(
            total[:-1].rjust(18) + ' ' * 12 + leader_slots_info[50:-1] + '◎{0:.3f}'.format(commission).rjust(13) + '\n')


####################################################################

'''MAIN PART (sazhiv)'''
print('Check balance\t- 1')
print('Leaderslots\t\t- 2')
print('Epoch info\t\t- 3')

identity = ['A1enabzLW77R2VVg67CLv3kNJ5FWVnAmC6pKcZwCmkXB', 'sh4rkGLyKwi8q1n8bwYkDiUC2n1cs6tbWSTGogd45d6']
vote = ['voteAipENjPHajaL8264qeNHvg28aHBqakojS1AoXsz', 'voteDNom5RVrC14QfYhjdj5AS2xD3cZ21QMoWqbiroe']

while True:
    cmd = input('Choose option: ')
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
    else:
        break
