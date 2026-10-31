User Topic
    │
    ▼
┌─────────────┐
│ PLAN NODE   │
│ Create      │
│ Search      │
│ Queries     │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ SEARCH NODE │◄─────┐
│ Search Web  │      │
│ Fetch URLs  │      │
│ Extract Text│      │
└──────┬──────┘      │
       │             │
       ▼             │
┌─────────────┐      │
│ SYNTHESIZE  │      │
│ Build       │      │
│ Report      │      │
└──────┬──────┘      │
       │             │
       ▼             │
┌─────────────┐      │
│ REVIEW NODE │      │
│ Score       │      │
│ Report      │      │
└──────┬──────┘      │
       │             │
   Score > 7?        │
    │       │        │
   Yes      No ----->│
    │       SEARCH AGAIN
    │    
    │   
    │
    ▼        
 ┌──────────┐
 │WRITE     │
 │Save MD   │
 └──────────┘