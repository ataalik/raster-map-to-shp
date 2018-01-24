for i in /home/ata/temp/ancient/*
do
    if test -f "$i"
    then
       ./cclabel.py "$i"
    fi
done
