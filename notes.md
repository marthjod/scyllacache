```bash
docker run --rm --name scylla --publish 9042:9042 -d scylladb/scylla
```

```cql
create keyspace cache with replication = {'class': 'SimpleStrategy', 'replication_factor' : 1};
use cache;
create table if not exists cache (key text primary key, val text);
select * from cache;
truncate cache;
select ttl (val) from cache;
```
