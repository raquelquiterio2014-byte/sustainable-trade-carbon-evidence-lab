import pandas as pd
import pytest
from core import calculate, validate_trade, digest, is_public_http_url, AIResponse
from audit import connect, add_review, list_reviews

def sample():
    return pd.DataFrame([dict(record_id='A',product='Steel',origin='Brazil',destination='EU',quantity_tonnes=10,production_tco2e_per_tonne=2,transport_tco2e=3,source_label='synthetic',source_url='',evidence_status='synthetic')])

def test_calculation():
    assert calculate(sample()).illustrative_total_tco2e.iloc[0] == 23

def test_negative_rejected():
    d=sample();d.loc[0,'quantity_tonnes']=-1
    assert validate_trade(d)

def test_duplicate_rejected():
    d=pd.concat([sample(),sample()],ignore_index=True)
    assert validate_trade(d)

def test_missing_column():
    assert validate_trade(sample().drop(columns=['record_id']))

def test_digest_stable():
    assert digest(b'a')==digest(b'a') and digest(b'a')!=digest(b'b')

def test_url():
    assert is_public_http_url('https://example.com/a')
    assert not is_public_http_url('file:///tmp/x')

def test_schema():
    a=AIResponse.model_validate({'summary':'Test','claims':[],'missing_evidence':[],'limitations':[]})
    assert a.summary=='Test'

def test_audit(tmp_path):
    con=connect(str(tmp_path/'test.db'))
    add_review(con,'e','a','approved','reviewer','checked')
    assert list_reviews(con)[0][4]=='approved'
    con.close()

def test_audit_rejects_invalid(tmp_path):
    con=connect(str(tmp_path/'test.db'))
    with pytest.raises(ValueError):add_review(con,'e','a','invalid','reviewer','')
    con.close()
