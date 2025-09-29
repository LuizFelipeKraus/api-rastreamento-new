from locust import HttpUser, task, between

class StressTest(HttpUser):
    wait_time = between(1, 2)

    @task
    def rastreamento_post(self):
        payload = {
            "idr": "79cc939b9506076a0e6bee37daeab975",
            "merNF": "361799",
            "cnpjTomador": "59064766000182",
            "modoJson":1
        }
        self.client.post("/rastreamento/v1.2/", json=payload)
