## Title
Webhook `shop` identity is not covered by the HMAC, enabling cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating an HMAC computed over the raw request body. The `shop-domain` header that the library reports to the app's webhook handler (and that the app uses to attribute the event to a tenant) is never included in the signed material. Any actor who can obtain one genuine, validly-signed webhook (e.g. by installing the app on their own store) can replay that exact body/HMAC pair while substituting an arbitrary `x-shopify-shop-domain` / `shopify-shop-domain` header, and the library will accept it and hand it to the app's handler as if it originated from the victim shop.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw HTTP body: [1](#0-0) 

`shop` is read straight from an attacker-controlled header with no cryptographic binding to the body or the HMAC: [2](#0-1) 

`Utils::HmacValidator.validate` verifies the signature exclusively against `to_signable_string` (i.e. the body), never incorporating `shop`: [3](#0-2) 

`Webhooks::Registry.process` then trusts `request.shop` for tenant attribution immediately after this body-only HMAC check succeeds: [4](#0-3) 

The identity binding that should hold is:
`shop header authenticated by HMAC == shop the app attributes the event to`

but in fact only `body bytes verified by HMAC == body bytes parsed` holds — the `shop` header is completely outside the cryptographic envelope. Because the same `api_secret_key` is used for every shop that installs the app, any merchant (an "unprivileged internet user" from the app's perspective — no special privilege beyond installing the app once) can capture one legitimately Shopify-signed webhook delivered for their own store, then POST that identical body + HMAC to the app's shared webhook endpoint while swapping the `shop-domain` header to any other installed shop's domain. `HmacValidator.validate` still succeeds because it only checks the body, and `Registry.process` forwards `WebhookMetadata.new(shop: request.shop, ...)` to the app's handler, which will act on it as if the payload genuinely came from the victim shop.

### Impact Explanation
This breaks the tenant-isolation guarantee the HMAC is supposed to provide for `ShopifyAPI::Webhooks`. Depending on how the consuming app's `WebhookHandler#handle` uses `data.shop` and `data.body`, this enables cross-tenant data confusion/injection: e.g. spoofing `app/uninstalled` for a victim shop to trigger deauthorization/deletion of the victim's stored session and tokens, or injecting attacker-controlled payload content (from the attacker's own store) tagged as belonging to the victim shop, corrupting per-tenant state. This matches the "Critical - cross-tenant access" impact category, since a webhook event can be forged against a shop the attacker does not control or have credentials for.

### Likelihood Explanation
Likelihood is high for any app that (a) exposes a single shared webhook endpoint for all installed shops (the standard pattern documented for this gem, see `Webhooks::Registry`/`Webhooks::Request`), and (b) is installable by low-trust/self-serve merchants (common for public Shopify apps). An attacker only needs to install the app once on a store they control to obtain one valid, freely reusable (body, HMAC) pair, then can replay it with an arbitrary `shop` header value at will — no access token, no `client_secret`, and no privileged Shopify access is required.

### Recommendation
Bind the `shop` (and ideally `topic`/`webhook-id`) into the value that is HMAC-verified, or otherwise cryptographically tie the header to the signed payload before trusting it for tenant attribution — for example, by having `to_signable_string` incorporate the shop domain, or by cross-checking `request.shop` against a shop that the app already knows is associated with a currently valid, previously-issued access token/session before processing the payload. At minimum, document prominently that `request.shop` is unauthenticated and must not be trusted for tenant attribution without an independent check.

### Proof of Concept
1. Attacker installs the target app on their own store `attacker-shop.myshopify.com`, triggering a real webhook, e.g.:
   - Headers: `x-shopify-hmac-sha256: <valid HMAC over body>`, `x-shopify-shop-domain: attacker-shop.myshopify.com`, `x-shopify-topic: orders/create`
   - Body: `{"id": 1, ...attacker-controlled order data...}`
2. Attacker captures this exact `(raw_body, hmac)` pair.
3. Attacker POSTs the same raw body and HMAC to the app's shared webhook endpoint, but replaces the header with `x-shopify-shop-domain: victim-shop.myshopify.com`.
4. `HmacValidator.validate` in `lib/shopify_api/utils/hmac_validator.rb` succeeds because it only checks `raw_body` against the HMAC — it never inspects `shop`.
5. `Webhooks::Registry.process` (`lib/shopify_api/webhooks/registry.rb:188-200`) invokes the app's handler with `shop: "victim-shop.myshopify.com"` and the attacker-supplied body, causing the app to process attacker-controlled data as if it were an authentic event from the victim's store.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L20-23)
```ruby
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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```

**File:** lib/shopify_api/webhooks/registry.rb (L188-200)
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
        end
```
