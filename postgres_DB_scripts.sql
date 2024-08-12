CREATE TABLE P21_companyreview (
    item_id VARCHAR(200),
    prefix VARCHAR(200),
    supplier_part_number VARCHAR(200),
    stripped_spn VARCHAR(200),
    matched_pricingdoc_SPN VARCHAR(200),
    prefix_check VARCHAR(200),
    on_vendor_price_book VARCHAR(200),
    on_latest_price_book VARCHAR(200),
    pb_check VARCHAR(200),
    cost VARCHAR(200),
    p1 VARCHAR(200),
    list_price VARCHAR(200),
    cost_on_vendorPB VARCHAR(200),
    p1_on_vendorPB VARCHAR(200),
    list_price_on_vendorPB VARCHAR(200),
    cost_check VARCHAR(200),
    p1_check VARCHAR(200),
    listprice_check VARCHAR(200),
    discrepancy_types VARCHAR(200)
);


create table Pricingreview (supplier_part_number varchar(60), matched_pricingdoc_SPN varchar(60), on_vendor_price_book varchar (10), cost float, p1 float, list_price float)