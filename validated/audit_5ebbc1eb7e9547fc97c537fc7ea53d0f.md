### Title
Webhook HMAC signature does not cover the `shop`, `topic`, `webhook-id` and `api-version` headers, allowing cross-tenant webhook forgery - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating the HMAC over the raw request body, then trusts the `shop-domain`, `topic`, `webhook-id`, and `api-version` HTTP headers — none of which are covered by that HMAC — to build the `WebhookMetadata` passed to the app's handler.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw body: [1](#0-0) 

The `shop`, `topic`, `webhook_id`, and `api_version` accessors are read straight from HTTP headers that are never mixed into the signable string: [2](#0-1) 

`HmacValidator.validate` only checks `hmac` against `to_signable_string`, i.e. only the body bytes: [3](#0-2) 

`Registry.process` treats a valid body HMAC as authorization to trust the header-derived `shop`, `topic`, and `webhook_id` when constructing `WebhookMetadata` for the handler: [4](#0-3) 

Shopify signs webhooks with the app's shared `client_secret` (`api_secret_key`), which is identical for every shop that has the app installed — it is not shop-specific. Because the signature binds only the body bytes and never the shop identity, the equality the gem implicitly relies on —

`shop claimed in header == shop that produced the signed body`

— is never actually checked. Any tenant that installs the app (an unprivileged internet user from the perspective of any *other* tenant) can trigger a legitimate webhook delivery for their own shop (e.g. by placing a test order, or via `orders/create`), capture the resulting `(raw_body, X-Shopify-Hmac-Sha256)` pair — both attacker-controlled or attacker-observable since it's their own store — and replay that exact body/HMAC pair to the app's webhook endpoint while substituting the `X-Shopify-Shop-Domain` (and/or topic/webhook-id) header with a victim shop's domain. `HmacValidator.validate` still succeeds because it only checks the (unmodified) body against the shared secret; `Registry.process` then dispatches the handler with `WebhookMetadata.shop` set to the attacker-chosen victim domain.

### Impact Explanation
This breaks the tenant boundary the gem is meant to enforce for webhook processing: an attacker who legitimately controls one shop installation can make the app's webhook handler act as though the event originated from a different, victim shop. In any host application that uses `WebhookMetadata#shop` to key per-tenant data updates, deletions (e.g. `app/uninstalled` triggering session/token cleanup), or entitlement logic, this enables cross-tenant data confusion/corruption using only the attacker's own valid installation — no credentials of the victim or the platform are required.

### Likelihood Explanation
Exploitation only requires the attacker to install the app in a shop they control (a normal, low-privilege capability for any Shopify merchant) and to be able to POST a captured body/HMAC pair with a modified `X-Shopify-Shop-Domain`/`X-Shopify-Topic`/`X-Shopify-Webhook-Id` header set to the app's public webhook endpoint. No secrets, tokens, or elevated access are needed, making this practically reachable by any unprivileged internet user who is also a legitimate (even free-trial) merchant of the app.

### Recommendation
Bind the header-derived identity fields into the value that is actually HMAC-verified, or otherwise cryptographically tie the `shop`, `topic`, and `webhook_id` to the signed payload (e.g., require and validate a per-shop signing secret, or include these headers in the canonical string that `HmacValidator` verifies) so that `WebhookMetadata.shop` cannot diverge from the shop whose body actually produced the valid signature.

### Proof of Concept
1. App is installed on `attacker-shop.myshopify.com` (attacker-controlled) and on `victim-shop.myshopify.com`.
2. Attacker triggers a webhook topic they can generate themselves (e.g. `orders/create`) on their own shop and captures the POST: `raw_body`, and header `X-Shopify-Hmac-Sha256: <valid signature over raw_body using the app's shared client_secret>`.
3. Attacker resends the exact same `raw_body` and `X-Shopify-Hmac-Sha256` value to the app's webhook endpoint, but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
4. `HmacValidator.validate` (`lib/shopify_api/utils/hmac_validator.rb:26-31`) succeeds because it only re-hashes `raw_body`.
5. `Registry.process` (`lib/shopify_api/webhooks/registry.rb:188-200`) invokes the handler with `WebhookMetadata.shop == "victim-shop.myshopify.com"`, even though the payload actually originated from the attacker's own shop.

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
