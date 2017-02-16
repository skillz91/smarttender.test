import httplib2
import json


class WebService:
    @staticmethod
    def execute(calc_id, args):
        request_args = json.dumps({
            "calcId": calc_id,
            "args": json.dumps(args),
            "ticket": ""
        })
        h = httplib2.Http()
        resp, content = h.request("http://test.smarttender.biz/ws/webservice.asmx/ExecuteEx?pureJSON=", method="POST",
                                              body=request_args,
                                              headers={"Content-Type": "application/json"})
        ret = json.loads(content, encoding="utf-8")
        return ret
