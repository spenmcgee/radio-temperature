# radio-temperature
Read radio temperature data from Lacrosse TX29 (?) transmitter using RTL-SDR

To Run: python decode.py <sample_rate> <decimation> <baud_rate> < rtl_sdr -f <center_freq> -g <gain> -s <sample_rate>

Example: python decode.py 2048000 10 4096 < rtl_sdr -f 433920000 -g 40 -s 2048000
