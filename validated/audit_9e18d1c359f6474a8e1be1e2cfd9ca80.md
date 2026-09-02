### Title
Webhook `shop` domain is not covered by the HMAC signature, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` derives the webhook's tenant identity (`shop`) from an HTTP header that is never included in the HMAC-signed content, while `ShopifyAPI::Webhooks::Registry.process` trusts that header value to build the `WebhookMetadata` handed to the app's handler. This breaks the intended binding: `hmac(raw_body) == valid` should imply `shop == the shop this payload actually belongs to`, but in this implementation `shop` is decoupled from the signed bytes entirely.

### Finding Description
`Utils::HmacValidator.validate` computes and checks the signature only over `verifiable_query.to_signable_string`: [1](#0-0) 

For webhook requests, `to_signable_string` is defined to be just the raw HTTP body: [2](#0-1) 

But `shop` is read from a completely separate header (`shopify-shop-domain` / `x-shopify-shop-domain`) that plays no part in the signable string: [3](#0-2) 

`Registry.process` validates the HMAC (which only proves the *body* bytes were signed with the app's shared secret) and then forwards the unverified `request.shop` straight to the app's handler as the tenant identifier: [4](#0-3) 

Because the `api_secret_key` used to sign webhook bodies is the single shared secret for the whole app (not per-shop), any merchant who has installed the app can legitimately receive a real `(raw_body, hmac)` pair for their own store. Nothing stops that merchant from replaying the identical `raw_body` + `hmac` to the app's webhook endpoint while substituting a different value in the `shop-domain` header. `HmacValidator.validate` will still return `true` (the body/HMAC pair is genuinely valid), and `Registry.process` will hand the handler a `WebhookMetadata` claiming the payload came from the victim shop.

Equality that should hold but doesn't: `shop_claimed_in_metadata == shop_the_signed_payload_actually_originated_from`. Before the attack this holds (each shop's webhook delivery carries its own shop header alongside its own body). After the attacker's replay with a doctored header, `shop_claimed_in_metadata` is attacker-controlled while `shop_the_signed_payload_actually_originated_from` remains the attacker's own shop — yet the HMAC check still passes because it never inspected `shop` at all.

### Impact Explanation
Any app built on this gem that uses `WebhookMetadata#shop` to key data writes, look up sessions/tenants, or drive business logic (a very common pattern) can be made to process data under a false tenant identity. This is a cross-tenant integrity/confidentiality issue: a low-privileged actor (a merchant who merely installed the app, i.e., an "unprivileged internet user" relative to other tenants) can inject or corrupt data attributed to a shop they do not own, without needing the app's `client_secret`, an access token, or any credential belonging to the victim.

### Likelihood Explanation
Likelihood is high for any app that relies on the gem's webhook shop attribution without independently re-validating it: the attacker only needs to be a legitimate (even free-trial) installer of the target app to obtain one genuine `(body, hmac)` pair, then can freely swap the `shop-domain` header value on replay. No secrets, tokens, or the app's `client_secret` are required.

### Recommendation
Include the shop domain (and ideally topic/webhook-id) inside the HMAC-covered signable content, or independently verify that the `shop-domain` header corresponds to a shop known to be subscribed to that specific webhook/topic before trusting `request.shop`. At minimum, document and enforce that `request.shop` must be cross-checked against the caller's own shop registry rather than treated as authenticated by `HmacValidator.validate`.

### Proof of Concept
1. App developer installs their own app on `attacker-shop.myshopify.com` and receives a legitimate webhook (e.g. `orders/create`) with headers:
   - `x-shopify-hmac-sha256: <valid-hmac-of-body>`
   - `x-shopify-shop-domain: attacker-shop.myshopify.com`
   - body: `{"id": 1, ...}`
2. Attacker resends the exact same body and `x-shopify-hmac-sha256` value to the app's webhook endpoint, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new` parses this successfully; `Utils::HmacValidator.validate` returns `true` because it only checks the body/HMAC pair. [5](#0-4) 
4. `Registry.process` invokes the app's handler with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", body: <attacker-controlled>, ...)`, so the app performs an operation against `victim-shop` data using attacker-supplied content — a cross-tenant write/read achieved with a signature the gem itself certified as valid.

### Citations

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

**File:** lib/shopify_api/webhooks/request.rb (L20-33)
```ruby
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

**File:** lib/shopify_api/webhooks/request.rb (L35-43)
```ruby
      sig { override.returns(String) }
      def to_signable_string
        @raw_body
      end

      sig { returns(T::Hash[String, T.untyped]) }
      def parsed_body
        JSON.parse(@raw_body)
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
