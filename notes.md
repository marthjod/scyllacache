```bash
docker run --rm --name scylla --publish 9042:9042 -d scylladb/scylla
docker exec -ti scylla cqlsh
```

```cql
create keyspace cache with replication = {'class': 'SimpleStrategy', 'replication_factor' : 1};
use cache;
create table cache (key text primary key, val text);

select * from cache;
truncate cache;
select ttl (val) from cache;
```
