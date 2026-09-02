Confirmed: the HMAC is computed only over `to_signable_string`, and for webhooks that value is exclusively `@raw_body` [1](#0-0) . The `shop`, `topic`, `api_version`, and `webhook_id` values are read straight from HTTP headers and are never part of the signed content [2](#0-1) . `Registry.process` accepts the request the moment `HmacValidator.validate` succeeds and then forwards the unauthenticated `shop` header straight into the app-facing `WebhookMetadata` used to route/attribute the event [3](#0-2) .

### Title
Webhook `shop` (tenant) identity is not covered by the HMAC, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/webhooks/registry.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` treats a webhook request as authentic for whatever `shop` is stated in the `x-shopify-shop-domain` / `shopify-shop-domain` header, but the HMAC that gates `process` only ever signs the raw body bytes, never the shop header. Any party capable of producing one valid `(body, hmac)` pair for the app's shared `client_secret` — e.g. their own store that has the app installed and legitimately receives signed webhooks — can replay that exact body/HMAC pair while swapping only the shop-domain header value, and the gem will accept it as coming from an arbitrary victim shop.

### Finding Description
`Webhooks::Request` implements `Utils::VerifiableQuery`, and its `to_signable_string` returns only `@raw_body`: [1](#0-0) 

Meanwhile `shop`, `topic`, `api_version`, and `webhook_id` are all pulled straight from request headers with no cryptographic binding: [2](#0-1) 

`Registry.process` validates only the HMAC (over the body) and then immediately trusts `request.shop` as the tenant identity, forwarding it into `WebhookMetadata` given to the app's handler: [3](#0-2) 

The identity equality the gem implicitly relies on is:

`shop asserted in header == shop that produced the HMAC-signed body`

But the HMAC secret (`Context.api_secret_key`, the app's single `client_secret`) is shared across every shop that has the app installed — it is not per-shop. This means a party who legitimately owns *any* shop installation of the app can capture a genuine, validly-signed webhook delivery (body + HMAC) sent to their own endpoint, then POST that exact same body/HMAC pair to the app's public webhook endpoint while substituting the `shop-domain` header with an arbitrary victim shop's domain. `HmacValidator.validate` still succeeds because it only recomputes the HMAC over the body via `verifiable_query.to_signable_string`: [4](#0-3) 

The app's handler then receives `WebhookMetadata` claiming `shop: <victim-shop>` with attacker-controlled body content, having passed HMAC validation — the gem provides no mechanism, and the documentation does not instruct callers, to verify that the header-asserted shop matches a shop actually associated with the signed payload.

### Impact Explanation
This breaks the tenant/identity boundary the HMAC check is meant to enforce: a request cryptographically proven to originate from the attacker's own shop is accepted by the library as authenticated data "from" a different, victim shop. Any app that keys persistence, redaction, entitlement, or business logic off `WebhookMetadata#shop` (exactly as `docs/usage/webhooks.md` and the mandatory `shop/redact`, `customers/redact`, `customers/data_request` topics instruct apps to do) can be made to process attacker-supplied data under a victim tenant's identity — i.e., cross-tenant access/data corruption via a spoofed identity binding, which the library asserts as verified.

### Likelihood Explanation
The webhook HTTP endpoint is, by design, a public, unauthenticated internet-facing endpoint (Shopify calls it with no other proof of origin than the HMAC header). Obtaining one valid `(body, hmac)` pair only requires access to a shop where the app is installed — including the attacker's own store, which any unprivileged internet user can obtain by installing a public app. No access to `api_secret_key`, access tokens, or the merchant's credentials is required.

### Recommendation
Do not treat header-only fields as authenticated. Either include `shop` (and ideally `topic`/`webhook-id`) in the HMAC-signable content, or require callers to validate the received `shop` against a shop that is independently known to be registered/installed (e.g. cross-check against stored sessions) before trusting `WebhookMetadata#shop`, and clearly document that today's `hmac` validation provides no shop-binding guarantee.

### Proof of Concept
1. Attacker installs the target app on their own store, `attacker.myshopify.com`, and configures a webhook subscription so Shopify delivers a real webhook, e.g. `orders/create`, to the app's public webhook endpoint.
2. Attacker's endpoint (or a network capture) records the exact raw request body `B` and the header `x-shopify-hmac-sha256: H`, where `H = HMAC-SHA256(client_secret, B)` — this HMAC is valid because `client_secret` is shared by the app across all installs, not scoped per shop.
3. Attacker crafts a new HTTP POST to the same webhook endpoint with:
   - Body: unchanged `B`
   - Header `x-shopify-hmac-sha256: H` (unchanged, still valid)
   - Header `x-shopify-shop-domain: victim-shop.myshopify.com` (swapped)
   - Header `x-shopify-topic: orders/create` (unchanged or freely chosen from registered topics)
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes the HMAC only over `request.to_signable_string` (`= B`) and succeeds, since only the body was verified. [5](#0-4) 
5. `Registry.process` builds `WebhookMetadata.new(topic: "orders/create", shop: "victim-shop.myshopify.com", body: <attacker's parsed body>, ...)` and passes it to the app's handler, which treats it as an authenticated event for `victim-shop.myshopify.com`. [6](#0-5)

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L15-23)
```ruby
      sig { returns(String) }
      def topic
        T.cast(shopify_header("topic"), String)
      end

      sig { returns(String) }
      def shop
        T.cast(shopify_header("shop-domain"), String)
      end
```

**File:** lib/shopify_api/webhooks/request.rb (L35-38)
```ruby
      sig { override.returns(String) }
      def to_signable_string
        @raw_body
      end
```

**File:** lib/shopify_api/webhooks/registry.rb (L188-199)
```ruby
        sig { params(request: Request).void }
        def process(request)
          raise Errors::InvalidWebhookError, "Invalid webhook HMAC." unless Utils::HmacValidator.validate(request)

          handler = @registry[request.topic]&.handler

          unless handler
            raise Errors::NoWebhookHandler, "No webhook handler found for topic: #{request.topic}."
          end

          handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop,
            body: request.parsed_body, api_version: request.api_version, webhook_id: request.webhook_id))
```

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```
