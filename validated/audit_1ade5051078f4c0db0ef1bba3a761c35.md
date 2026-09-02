### Title
Webhook shop-tenant identity is taken from an unsigned HTTP header while the HMAC only signs the request body - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by verifying the HMAC over the raw request body, but the shop that the webhook is attributed to (`request.shop`) is read straight from the unauthenticated `x-shopify-shop-domain` HTTP header, which is never part of the signed payload. Because the app's webhook HMAC secret (`api_secret_key`) is shared across *every* shop that has the app installed, an attacker who merely installs the app on their own store can capture one of their own legitimately-signed webhooks and replay it with the `shop-domain` header swapped to a victim shop, producing a request that passes HMAC validation but is attributed to the victim's tenant.

### Finding Description
The webhook `Request` object builds its signable string from only the raw body: [1](#0-0) 

`shop`, `topic`, `webhook_id`, and `api_version` are all pulled from HTTP headers, but only the body is fed into `to_signable_string`: [2](#0-1) 

`HmacValidator.validate` computes `HMAC(secret, body)` and compares it to the `hmac-sha256` header — it has no knowledge of, and does not cover, the shop header at all: [3](#0-2) 

`Registry.process` then trusts this unauthenticated header as the tenant identity for dispatch: [4](#0-3) 

The identity binding that should hold is:
`shop_the_HMAC_was_computed_for == shop_the_handler_acts_on`

But the actual binding enforced by the code is only:
`HMAC(secret, body) == received_hmac`

with `shop` entirely outside that equation. Since `api_secret_key` is one value per app (not per install), any store owner who installs the app receives webhooks HMAC'd with the *same* secret used for all other installs. That means a legitimate webhook body+HMAC pair captured from the attacker's own store's install is a valid body+HMAC pair for *any* shop, because the signature never encodes which shop it belongs to. Swapping the `x-shopify-shop-domain` (or `shopify-shop-domain`) header on a replayed request changes the effective tenant without invalidating the signature.

### Impact Explanation
This breaks the tenant isolation the HMAC check is meant to provide. An attacker (any unprivileged merchant who can install the app on their own store) can make the host application's webhook handler execute with `shop == <victim shop>` while supplying attacker-controlled body content, or replay a captured webhook (e.g. `app/uninstalled`, `shop/update`) tagged as a victim shop to trigger tenant-scoped side effects (session teardown, data updates, billing state changes, etc.) for a shop the attacker does not control. This is a cross-tenant access impact, since the gem hands the host app data purportedly belonging to one merchant while it actually originated from a different, unauthenticated source.

### Likelihood Explanation
Likelihood is high for any app author who trusts `WebhookMetadata#shop` (built directly from `request.shop`) as an authenticated tenant identifier, which is the intended and documented usage pattern of `Registry.process`/`WebhookMetadata`. The only prerequisite is the ability to install the app on any store (including a free/dev store) to receive one genuinely HMAC-signed webhook and then replay it with a modified shop header — no `api_secret_key`, access token, or privileged account for the *victim* shop is required.

### Recommendation
Include the shop domain (and ideally topic/webhook id) in the HMAC-covered signable string, or otherwise cryptographically bind the header-derived `shop` to the signed body (e.g., verify the shop against a `WEBHOOK` record fetched via an authenticated API using the `webhook_id`, or require the caller to pass a previously-registered/known shop for verification) before dispatching to handlers in `Registry.process`.

### Proof of Concept
1. Attacker installs the app on `attacker-shop.myshopify.com` (no special privilege needed, just a store).
2. Shopify sends a legitimate webhook to the app's callback URL:
   - Headers: `x-shopify-shop-domain: attacker-shop.myshopify.com`, `x-shopify-hmac-sha256: <valid HMAC over BODY using the app's shared api_secret_key>`, body `BODY`.
3. Attacker captures this request and re-sends it to the same endpoint, only replacing the header:
   - `x-shopify-shop-domain: victim-shop.myshopify.com`
   - Same `BODY` and same `x-shopify-hmac-sha256` value (still valid, since HMAC only signed `BODY`).
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)` — passes, because the HMAC only checked `BODY` against the shared secret: [5](#0-4) 
5. The handler receives `WebhookMetadata.new(topic: ..., shop: "victim-shop.myshopify.com", body: <attacker-controlled parsed body>, ...)` and the host application processes it believing it is authentic data from `victim-shop`.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-23)
```ruby
      sig { override.returns(String) }
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
      end

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
