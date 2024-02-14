this folder consists of:
1. Python file:
    1. <Place_Order_V2.py>
    2. <Download_Order_V2.py>

2.JSON files for inputs:
    1.<search_config_file.json>    edit search criteria
    2.<login_parameters.json>      login credentials


* functions in "Place_Order_V2.py" "script:
    a func. to save the order infro to csv file for later use <order_info_tocsv>
    a func. to Get the order number placed <get_ticket_order_no>
    a func. to LOGIN <login>
    a func. to detect place on Map <map_point>
    a func. to select Order Criteria <order_criteria>
    a func. to make the order <place_order>
    a func. to get search criteria from the config file <pars_mapdata_from_cnfg_file>





* functions in  "Download_Order_V2.py" "script:
    a func. to download images of the ready order <download_files>
    a func. to upload downloaded images to S3 <uploading_to_s3>
    a func. to LOGIN <login>
    a func. check a given order number is ready for download <check_order_status>




output will be saved to:

                "bucket_name/stand_alone/CLASS/Satellite_name/"Order Number"/"
    example:

                "s3://rfims-prototype/stand_alone/CLASS/NOAA-18/8357663145/NSS.HRPT.NN.D23311.S0558.E0609.B9517878.MO"




Usage:
1. conda activate pytorch_p39
2. python /location of the file/Place_Order_V2.py
3. python /location of the file/Download_Order_V2.py


Another way is to call attached bash file
1. ./location of the file/place_order.sh
2. ./location of the file/download_order.sh


