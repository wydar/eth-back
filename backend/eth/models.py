from django.db import models


class Station(models.Model):
    """
    Station model
    """
    station_id = models.IntegerField(primary_key=True)
    contract_address = models.CharField(max_length=150, null=True, blank=True)
    contract_abi = models.TextField(null=True, blank=True)
    contract_byte_code = models.TextField(null=True, blank=True)
    is_active = models.BooleanField(null=True, blank=True, default=True)

    def __str__(self):
        return str(self.pk)


class Measures(models.Model):
    """
    Measures model
    """
    temperature = models.DecimalField(max_digits=6, decimal_places=3, null=False, blank=False)
    humidity = models.DecimalField(max_digits=6, decimal_places=3, null=False, blank=False)
    altitude = models.DecimalField(max_digits=6, decimal_places=3, null=False, blank=False)
    preassure = models.DecimalField(max_digits=6, decimal_places=3, null=False, blank=False)
    timestamp = models.DecimalField(max_digits=6, decimal_places=3, null=False, blank=False)

    def save(self, *args, **kwargs):
        self.temperature = self.temperature / 100
        self.humidity = self.humidity / 100
        self.altitude = self.altitude / 100
        self.preassure = self.preassure / 100
        super().save(*args, **kwargs)

    def __str__(self):
        return self.pk
