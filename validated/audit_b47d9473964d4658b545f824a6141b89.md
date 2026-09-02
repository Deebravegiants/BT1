### Title
Webhook shop identity spoofing via HMAC that does not cover the `shop-domain` header - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` derives the tenant identity (`shop`) exclusively from the unauthenticated `X-Shopify-Shop-Domain` HTTP header, while the HMAC signature that `Webhooks::Registry.process` verifies is computed only over the raw request body. Because the shop identifier is never part of the signed payload, an attacker who possesses one validly-signed webhook body (trivially obtainable by triggering an event on their own store, which anyone can create for free) can replay that exact body to the app's webhook endpoint while substituting the `X-Shopify-Shop-Domain` header for an arbitrary victim shop. The signature still validates, and the handler processes the payload attributing it to the victim tenant — a cross-tenant identity-binding break of the same class as the reported "field acted on but not covered by the HMAC" bug class.

### Finding Description
`Webhooks::Request` implements `Utils::VerifiableQuery` and defines: [1](#0-0) 

`shop` is read straight from the `shopify-shop-domain` / `x-shopify-shop-domain` header, but `to_signable_string` — the value that is actually HMAC-verified — is just `@raw_body`. The `shop` value is never mixed into the signed string.

`Webhooks::Registry.process` verifies the HMAC and then trusts `request.shop` directly when building the data passed to the app's handler: [2](#0-1) 

`Utils::HmacValidator.validate` only checks that `hmac` matches `compute_signature(verifiable_query.to_signable_string, secret)`: [3](#0-2) 

Since `to_signable_string` for a webhook request is the raw body only (not headers), **the identity binding "shop-domain header == shop that the HMAC was computed for" does not hold**: the HMAC only proves body integrity, not which shop the event originated from. This is exactly the report's hinted bug class: *"a field acted on but not covered by the HMAC."* Here the "field acted on" is `shop`, consumed by `WebhookMetadata.shop` and passed into the app's `handler.handle`.

### Impact Explanation
An unprivileged internet user who owns any Shopify shop (including a free/dev store) can:
1. Trigger a legitimate webhook event (e.g., `orders/create`, `customers/data_request`, `app/uninstalled`) on their own shop, which Shopify signs correctly with the app's shared secret over the raw JSON body — the attacker never needs `api_secret_key` itself, only a validly-signed body that Shopify sends them.
2. Replay that raw body + HMAC unmodified to the target app's public webhook endpoint, but with the `X-Shopify-Shop-Domain` header rewritten to a victim shop's domain.
3. `HmacValidator.validate` still succeeds because it only checks the (unchanged) body against the HMAC.
4. `Registry.process` calls the handler with `shop: request.shop` set to the victim's domain, causing the app to act on/attribute data as if the event happened on the victim's tenant.

This is a cross-tenant identity confusion: the equality that should hold — `shop bound by HMAC == shop delivered to handler` — is broken, because the HMAC binds nothing about `shop`. Depending on what the hosting app does with `WebhookMetadata.shop` (e.g., look up/update a session, mark a shop uninstalled, process a GDPR redact request, write data keyed by shop), this can cause cross-tenant data corruption or privacy actions being applied to the wrong tenant — satisfying the "cross-tenant access" Critical impact class.

### Likelihood Explanation
Likelihood is meaningful but bounded: the attacker must possess or control at least one Shopify shop capable of generating a validly-signed webhook (readily achievable via a free/dev store), and the target app must expose its webhook endpoint publicly (a documented requirement of this gem's `Registry.process` flow). No secret key, token, or victim credentials are required — only replaying a header value on an otherwise legitimate signed request. This is a straightforward and repeatable attack for any developer with a Shopify partner/dev account.

### Recommendation
Include the shop domain (and ideally other identifying headers, e.g., `api-version`, `webhook-id`, `topic`) in the value that is HMAC-verified, or otherwise cryptographically bind the `shop-domain` header to the signed payload before trusting it in `Webhooks::Registry.process`. At minimum, document and enforce that consuming apps must not rely on `WebhookMetadata.shop` as an authenticated tenant identifier unless it is cross-checked against a shop already known to be associated with the webhook's HMAC-covered content (e.g., an embedded shop ID in the body) or the topic-specific mandatory GID.

### Proof of Concept
```
# 1. Attacker owns "attacker-shop.myshopify.com" and installs the target app.
# 2. Attacker triggers a real event, e.g. creates an order, causing Shopify to
#    POST a correctly-signed webhook to the app's endpoint:
POST /webhooks
X-Shopify-Topic: orders/create
X-Shopify-Hmac-Sha256: <valid-hmac-for-body>
X-Shopify-Shop-Domain: attacker-shop.myshopify.com
Body: {"id": 123, ...}

# 3. Attacker captures this exact raw body + hmac header, then replays it,
#    only changing the shop-domain header to the victim shop:
POST /webhooks
X-Shopify-Topic: orders/create
X-Shopify-Hmac-Sha256: <same-valid-hmac-for-same-body>   # still valid since body unchanged
X-Shopify-Shop-Domain: victim-shop.myshopify.com
Body: {"id": 123, ...}                                    # unchanged

# 4. ShopifyAPI::Webhooks::Registry.process(request) validates:
#    Utils::HmacValidator.validate(request) -> true (body-only check, passes)
# 5. handler.handle(data: WebhookMetadata.new(topic: ..., shop: "victim-shop.myshopify.com", ...))
#    is invoked, causing the app to process/attribute the event as belonging to the victim tenant.
``` [4](#0-3) [2](#0-1)

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-38)
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

      sig { returns(String) }
      def api_version
        T.cast(shopify_header("api-version"), String)
      end

      sig { returns(String) }
      def webhook_id
        T.cast(shopify_header("webhook-id"), String)
      end

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L12-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery).returns(T::Boolean) }
        def validate(verifiable_query)
          return false unless verifiable_query.hmac

          result = validate_signature(verifiable_query, Context.api_secret_key)
          if result || Context.old_api_secret_key.nil? || T.must(Context.old_api_secret_key).empty?
            result
          else
            validate_signature(verifiable_query, T.must(Context.old_api_secret_key))
          end
        end

        private

        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```
