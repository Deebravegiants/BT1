### Title
Webhook `shop-domain` Header Is Not Covered by HMAC Verification, Enabling Cross-Tenant Webhook Spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` claims to "verify the request did indeed come from Shopify" before dispatching to the app's handler, but the HMAC verification only covers the raw request body — not the `shopify-shop-domain` / `x-shopify-shop-domain` header. The `shop` value handed to the app's `WebhookHandler` is therefore an unauthenticated field, breaking the equality between "shop whose HMAC was verified" and "shop the handler is told to act on."

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`ShopifyAPI::Webhooks::Request#shop` simply reads the `shop-domain` header without any cryptographic binding to that body: [2](#0-1) 

`Utils::HmacValidator.validate` computes the HMAC exclusively over `verifiable_query.to_signable_string` (i.e., the raw body) and compares it to the `hmac` header value — the shop header never enters the signature computation: [3](#0-2) 

`Webhooks::Registry.process` only checks this body HMAC, then immediately forwards `request.shop` (the unauthenticated header) to the app handler as the tenant identifier: [4](#0-3) 

The identity binding that should hold is:
`shop_whose_secret_produced_this_HMAC == shop_the_handler_is_told_the_event_belongs_to`

Because the header is excluded from the signable string, this equality is not enforced by the gem. An attacker who legitimately installs the app on their own shop (Shop A) will receive genuine Shopify-signed webhooks (HMAC computed over the body using the app's shared `client_secret`). Since the HMAC only depends on the body — not on which shop it was sent to — the attacker can replay that exact body + HMAC pair to the app's webhook endpoint while substituting an arbitrary `x-shopify-shop-domain` header (e.g., a victim shop, Shop B). `HmacValidator.validate` still succeeds (body/HMAC pair is valid), and `Registry.process` calls the handler with `shop: "shop-b.myshopify.com"` even though the payload actually originated from Shop A.

The gem's own documentation reinforces that host apps are meant to treat `data.shop` as trustworthy once `Registry.process` succeeds ("This will verify the request did indeed come from Shopify..."), and the sample handler code passes `data.shop` directly into business logic (`perform_later(topic: data.topic, shop_domain: data.shop, ...)`), so this is the gem's own documented, intended contract — not a misuse by the host app.

### Impact Explanation
This breaks the cross-tenant boundary that `Registry.process`/`HmacValidator` is supposed to enforce: a request that is cryptographically valid for Shop A's payload can be attributed to any other shop the attacker chooses in the header, letting an attacker inject fabricated (but validly-signed) webhook data under another merchant's identity into apps that key their processing (e.g., data updates, session lookups, job dispatch) off `data.shop`. This matches the "shop authenticated versus the shop stored/acted upon" cross-tenant analog called out in scope.

### Likelihood Explanation
Requires only that the attacker control one legitimately-installed shop for the app (a normal, unprivileged capability — anyone can install a public app on a free dev/trial store) and be able to POST arbitrary headers to the app's public webhook endpoint, which is by definition internet-reachable. No access token, `client_secret`, or privileged account is needed.

### Recommendation
Include the shop domain (and ideally topic/webhook-id) in the signable string used for HMAC verification, or otherwise cryptographically bind the `shop-domain` header to the verified body before exposing it to the handler, so that `HmacValidator.validate` fails if the shop header is swapped for a different, still-genuinely-signed payload.

### Proof of Concept
1. Install the target app (using this gem) on attacker-controlled Shop A; trigger a webhook (e.g. `orders/create`) so Shopify sends `POST /callback/orders/create` with body `B` and a valid `x-shopify-hmac-sha256` header `H` computed by Shopify over `B` using the app's `client_secret`.
2. Capture `B` and `H` from the genuine request (attacker owns the receiving endpoint/logs for their own shop).
3. Replay a new request to the same webhook endpoint: same body `B`, same `x-shopify-hmac-sha256: H`, but set `x-shopify-shop-domain: victim-shop.myshopify.com`.
4. `ShopifyAPI::Utils::HmacValidator.validate` succeeds because it only checks `B` against `H`; `ShopifyAPI::Webhooks::Registry.process` calls the app handler with `WebhookMetadata#shop == "victim-shop.myshopify.com"` even though the data came from Shop A, as shown in [5](#0-4) .

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
