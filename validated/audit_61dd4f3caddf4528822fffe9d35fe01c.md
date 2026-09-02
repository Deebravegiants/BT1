### Title
Webhook shop/topic/webhook-id headers are not covered by the HMAC signature, enabling cross-tenant webhook forgery - (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/webhooks/registry.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` only returns the raw request body, so the HMAC signature validated by `HmacValidator` binds *only* the body bytes. The identity fields the library then trusts — `shop`, `topic`, `webhook_id`, `api_version` — are read straight from HTTP headers that are excluded from that signature. Any party who can obtain one validly-signed webhook delivery (e.g. a legitimate low-privilege merchant who installs the app on their own store) can replay the exact same signed body while swapping the `X-Shopify-Shop-Domain` header to a different, victim tenant's domain, and the signature check will still pass.

### Finding Description
`Utils::HmacValidator.validate` computes `compute_signature(verifiable_query.to_signable_string, secret)` and compares it against the `hmac` field: [1](#0-0) 

For webhooks, `to_signable_string` is defined to return only `@raw_body`: [2](#0-1) 

Meanwhile `shop`, `topic`, `webhook_id`, and `api_version` are pulled from headers that are never mixed into the signed string: [3](#0-2) 

`Registry.process` validates the HMAC and then trusts `request.shop` (and `request.topic`) as the tenant identity forwarded to the app's handler, without any additional binding to the signed payload: [4](#0-3) 

Because the HMAC key (`Context.api_secret_key`) is the app's single `client_secret`, shared across every shop that installs the app, the signature over a given raw body is identical no matter which shop it is claimed to originate from. This breaks the identity binding `signed(shop) == trusted(shop)` that `Registry.process` implicitly assumes: the equality that should hold is `hmac_covers(shop_header) == true`, but in fact `hmac_covers(shop_header) == false`.

This mirrors the analog bug class described in the report: a value used by downstream logic (`validPriceList`/median index vs. array bounds; here, `request.shop`/`request.topic` vs. the HMAC-signed bytes) is not the value actually validated.

### Impact Explanation
An attacker who is a legitimate (but unprivileged, relative to other tenants) installer of the app on their own shop can:
1. Trigger any webhook topic on their own store to get one validly-signed `(body, hmac)` pair from Shopify.
2. Replay that same body/hmac to the app's webhook endpoint while changing `X-Shopify-Shop-Domain` (and optionally `X-Shopify-Topic`/`X-Shopify-Webhook-Id`) to a victim shop's domain.
3. `Registry.process` still calls `Utils::HmacValidator.validate(request)` successfully (body/signature match), then invokes the registered handler with `WebhookMetadata.new(topic: ..., shop: <victim shop>, body: ..., ...)`.

Any app logic that uses `webhook.shop` to look up, create, or mutate per-tenant records (which is the documented and expected usage pattern of `WebhookMetadata`) will act on the wrong tenant's data using attacker-controlled body content — this is a cross-tenant data integrity/injection issue reachable purely through this gem's own webhook processing code, without needing the app's `client_secret`, an access token, or any privileged account.

### Likelihood Explanation
Likely reachable in any app that: (a) exposes a webhook endpoint using `ShopifyAPI::Webhooks::Registry.process`, and (b) is multi-tenant (accepts installs from more than one shop) — which is the standard Shopify app model. The only prerequisite is that the attacker be able to install the app on at least one shop of their own (a very low bar, satisfying the "unprivileged internet user" framing relative to other tenants) and be able to send an arbitrary HTTP request with custom headers to the app's public webhook endpoint.

### Recommendation
Include the identity-critical headers (`shop-domain`, `topic`, `webhook_id`, `api_version`) in the signable string used for HMAC verification, or otherwise cryptographically bind them to the payload (e.g. verify `request.shop` against the destination shop expected for the given webhook subscription, or require the caller to separately corroborate the shop via a signed source such as an authenticated session). At minimum, document clearly that `request.shop`/`request.topic` are unauthenticated header values and must not be trusted for tenant-scoping decisions without independent verification.

### Proof of Concept
1. Legitimate app installs on `attacker-shop.myshopify.com`; Shopify sends a real webhook:
```
POST /webhooks
X-Shopify-Topic: orders/create
X-Shopify-Hmac-Sha256: <valid-hmac-of-body>
X-Shopify-Shop-Domain: attacker-shop.myshopify.com
X-Shopify-Webhook-Id: ...
Body: {"id": 1, ...attacker-controlled order payload...}
```
2. Attacker replays the identical body and `X-Shopify-Hmac-Sha256` value, only changing the domain header:
```
POST /webhooks
X-Shopify-Topic: orders/create
X-Shopify-Hmac-Sha256: <same-valid-hmac-of-same-body>
X-Shopify-Shop-Domain: victim-shop.myshopify.com
X-Shopify-Webhook-Id: ...
Body: {"id": 1, ...same attacker-controlled payload...}
```
3. `ShopifyAPI::Webhooks::Request.new` accepts it (all required headers present), `Utils::HmacValidator.validate` returns `true` because it only recomputes HMAC over `@raw_body`, and `Registry.process` invokes the app's handler with `shop: "victim-shop.myshopify.com"`, `body: <attacker payload>` — data intended for `victim-shop` is processed using attacker-controlled content that was never actually sent by `victim-shop` or Shopify on `victim-shop`'s behalf.

### Citations

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```

**File:** lib/shopify_api/webhooks/request.rb (L15-33)
```ruby
      sig { returns(String) }
      def topic
        T.cast(shopify_header("topic"), String)
      end

      sig { returns(String) }
      def shop
        T.cast(shopify_header("shop-domain"), String)
      end

      sig { returns(String) }
      def api_version
        T.cast(shopify_header("api-version"), String)
      end

      sig { returns(String) }
      def webhook_id
        T.cast(shopify_header("webhook-id"), String)
      end
```

**File:** lib/shopify_api/webhooks/request.rb (L35-38)
```ruby
      sig { override.returns(String) }
      def to_signable_string
        @raw_body
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
