This confirms the vulnerability: `WebhookMetadata.shop` [1](#0-0)  is passed to every host-app `WebhookHandler.handle` as the trusted tenant identifier, but that value originates entirely from the unauthenticated `shopify-shop-domain` HTTP header [2](#0-1) , while `Registry.process` only checks the HMAC before forwarding it [3](#0-2) .

### Title
Webhook shop-domain identity spoofing via HMAC that only covers the raw body - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body, and `HmacValidator.validate` verifies the HMAC solely against that body [4](#0-3) [5](#0-4) . The `shop` (and `topic`, `webhook_id`, `api_version`) values are read straight from HTTP headers and are never included in the signed bytes [6](#0-5) . `Registry.process` forwards `request.shop` unchanged into `WebhookMetadata` after only checking the body HMAC [3](#0-2) .

### Finding Description
The binding that should hold is: `shop domain authenticated by HMAC == shop domain the host app acts on`. Here that equality is broken — the bytes verified (raw body) are not the bytes the app uses to select the tenant (the `shop-domain` header). Any caller who can produce a body+HMAC pair that verifies with the app's `api_secret_key` (e.g., a merchant who has installed the app on their own store and receives a genuine webhook for that store) can resend the identical body/HMAC pair to the app's public webhook endpoint while substituting an arbitrary `x-shopify-shop-domain` header. `HmacValidator.validate` still returns true because it never inspects the header, and `Registry.process` hands `WebhookMetadata.new(shop: request.shop, ...)` to the app-defined `WebhookHandler#handle` as if it were an authenticated fact [7](#0-6) .

### Impact Explanation
This is a cross-tenant identity-spoofing primitive at the shopify_api layer: the gem hands the host application a `shop` value that looks authenticated (it survived HMAC validation) but is not bound to the signed payload at all. Any application logic that keys data storage, entitlement checks, or state transitions off `WebhookMetadata#shop` (which is the documented/intended usage of this struct) is exposed to cross-tenant confusion — an attacker-controlled store can cause the app to write, delete, or act on data under a victim shop's identity.

### Likelihood Explanation
Requires only an internet-reachable webhook endpoint plus the ability to obtain one genuine signed webhook body (trivial for any merchant who installs the app on a store they control, since Shopify sends real webhooks to every installer). No access token, `api_secret_key`, or privileged account is needed — only capturing one's own legitimately-delivered webhook and replaying it with a modified header.

### Recommendation
Include the authenticating identity fields (at minimum `shop`, and ideally `topic`/`webhook_id`) in the signable string, or otherwise cryptographically bind them to the HMAC, so `to_signable_string` cannot be satisfied by body-only replay with a swapped `shop-domain` header. Alternatively, document loudly (and enforce in `Registry.process`) that `WebhookMetadata#shop` must never be trusted as authenticated unless the header is independently validated (e.g., cross-checked against a shop known to have this webhook registered).

### Proof of Concept
1. Attacker installs the target app on `attacker.myshopify.com`; Shopify sends a real webhook: body `B`, header `x-shopify-hmac-sha256: HMAC(secret, B)`, `x-shopify-shop-domain: attacker.myshopify.com`.
2. Attacker resends the exact same body `B` and HMAC header to the app's public webhook endpoint, but sets `x-shopify-shop-domain: victim.myshopify.com`.
3. `HmacValidator.validate` in `lib/shopify_api/utils/hmac_validator.rb` recomputes `HMAC(secret, B)` and it matches — validation passes because the header is never part of the signed input [8](#0-7) .
4. `Registry.process` calls the registered handler with `WebhookMetadata.new(shop: "victim.myshopify.com", ...)`, and the host app performs its webhook side effects as if the event genuinely originated from `victim.myshopify.com` [3](#0-2) .

### Citations

**File:** lib/shopify_api/webhooks/webhook_handler.rb (L6-12)
```ruby
    class WebhookMetadata < T::Struct
      const :topic, String
      const :shop, String
      const :body, T::Hash[String, T.untyped]
      const :api_version, String
      const :webhook_id, String
    end
```

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L12-21)
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
