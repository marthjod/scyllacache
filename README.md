```bash
$ docker run --rm --name scylla --publish 9042:9042 -d scylladb/scylla
$ docker exec -ti scylla cqlsh
$ grep localhost /tmp/prometheus.yml
    - targets: ['localhost:8000']
$ docker run --net host --rm --name prom -p 9090:9090 -v /tmp/prometheus.yml:/etc/prometheus/prometheus.yml prom/prometheus
```

```cql
create keyspace cache with replication = {'class': 'SimpleStrategy', 'replication_factor' : 1};
use cache;
create table cache (key text primary key, val text);

select * from cache;
select ttl (val) from cache;
```

metrics

- cache get/put: http://localhost:9090/graph?g0.range_input=15m&g0.stacked=0&g0.expr=rate(scyllacache_cache_latency_seconds_sum%7Bop%3D%22get%22%7D%5B5m%5D)%20%2F%20rate(scyllacache_cache_latency_seconds_count%7Bop%3D%22get%22%7D%5B5m%5D)&g0.tab=0&g1.range_input=15m&g1.stacked=0&g1.expr=rate(scyllacache_cache_latency_seconds_sum%7Bop%3D%22put%22%7D%5B5m%5D)%20%2F%20rate(scyllacache_cache_latency_seconds_count%7Bop%3D%22put%22%7D%5B5m%5D)&g1.tab=0
- (un-)pickle: http://localhost:9090/graph?g0.range_input=15m&g0.expr=rate(scyllacache_pickle_latency_seconds_sum%7Bop%3D%22pickle%22%7D%5B5m%5D)%20%2F%20rate(scyllacache_pickle_latency_seconds_count%7Bop%3D%22pickle%22%7D%5B5m%5D)&g0.tab=0&g1.range_input=15m&g1.expr=rate(scyllacache_pickle_latency_seconds_sum%7Bop%3D%22unpickle%22%7D%5B5m%5D)%20%2F%20rate(scyllacache_pickle_latency_seconds_count%7Bop%3D%22unpickle%22%7D%5B5m%5D)&g1.tab=0
- backend read/write: http://localhost:9090/graph?g0.range_input=15m&g0.expr=rate(scyllacache_backend_latency_seconds_sum%7Bop%3D%22read%22%7D%5B5m%5D)%20%2F%20rate(scyllacache_backend_latency_seconds_count%7Bop%3D%22read%22%7D%5B5m%5D)&g0.tab=0&g1.range_input=15m&g1.expr=rate(scyllacache_backend_latency_seconds_sum%7Bop%3D%22write%22%7D%5B5m%5D)%20%2F%20rate(scyllacache_backend_latency_seconds_count%7Bop%3D%22write%22%7D%5B5m%5D)&g1.tab=0
