### Title
Webhook `shop` and `topic` identifiers are not covered by the HMAC, allowing cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an incoming webhook solely via `Utils::HmacValidator.validate(request)`, then forwards `request.shop` and `request.topic` to the app's handler as trusted, tenant-identifying values. But the HMAC only covers the raw request body — the `shop` and `topic` values come from HTTP headers that are excluded from the signed content, so they carry no cryptographic binding to the signature that was just "validated."

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`shop` and `topic` are read straight from the `x-shopify-shop-domain` / `x-shopify-topic` headers, independent of the signed body: [2](#0-1) 

`Registry.process` validates the HMAC and, once it passes, unconditionally trusts `request.topic` and `request.shop` to build the `WebhookMetadata` handed to the app's handler: [3](#0-2) 

`WebhookMetadata.shop` is a plain `String` field that host applications are expected to use as the tenant key when acting on webhook data (e.g., looking up the merchant's stored session/access token, or fulfilling `shop/redact`/`customers/redact`/`customers/data_request` mandatory compliance topics): [4](#0-3) 

The identity binding broken here is: `HMAC-verified(raw_body) == true` is treated as proof that `shop header == originating shop`, but the equality that actually holds is only `HMAC(raw_body, api_secret_key) == received_hmac`; the `shop`/`topic` headers are parsed, not verified.

### Impact Explanation
The app's shared `api_secret_key` is used to sign webhooks for every shop that has installed the app, not a per-shop secret. A merchant who installs the app receives genuine webhooks (valid `raw_body` + `hmac-sha256`) addressed to their own shop. Because the signature never covers the `shop-domain` or `topic` headers, that same merchant (an unprivileged actor with respect to any other tenant) can replay a captured, validly-signed body to the app's webhook endpoint while substituting the `x-shopify-shop-domain` header for a victim shop. `Utils::HmacValidator.validate` will still return `true` (it only checks body bytes against the secret), and `Registry.process` will dispatch a `WebhookMetadata` claiming to originate from the victim shop. Any handler logic keyed on `data.shop` — updating stored merchant records, triggering `customers/redact`/`shop/redact` GDPR flows, or writing to a per-shop data store — would then act on/for the wrong tenant. This is a cross-tenant integrity break traceable directly to the gem's webhook verification code.

### Likelihood Explanation
Exploitation requires only: (1) attacker's own working install of the target app (any storefront can install a public app), (2) capturing one legitimate webhook body+HMAC pair addressed to their own shop, and (3) replaying it to the app's public webhook endpoint with a modified `shop-domain` header — no access to `api_secret_key`, access tokens, or any privileged account is needed. This is squarely within the "unprivileged internet user" threat model.

### Recommendation
Bind `shop` (and ideally `topic`, `webhook_id`, `api_version`) into the value that is HMAC-verified, or otherwise cryptographically tie the header-derived shop domain to the signed payload before it is exposed via `WebhookMetadata`. At minimum, `HmacValidator`/`Request#to_signable_string` should incorporate the `shop-domain` header (and any other headers the app logic trusts) into the signed string, so that spoofing the header invalidates the signature.

### Proof of Concept
1. Attacker installs the target Shopify app on `attacker-shop.myshopify.com`, receiving genuine webhooks signed with the app's shared `api_secret_key`.
2. Attacker captures a delivered webhook: raw body `B` and header `x-shopify-hmac-sha256: H` (valid because `HMAC-SHA256(api_secret_key, B) == H`), plus `x-shopify-topic: orders/create` (or `customers/redact`).
3. Attacker POSTs to the app's webhook endpoint with the same body `B` and `hmac-sha256: H`, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
4. `Utils::HmacValidator.validate(request)` returns `true` because it only checks `B` against `H`: [5](#0-4) 
5. `Registry.process` builds `WebhookMetadata.new(shop: "victim-shop.myshopify.com", topic: ..., body: parsed(B), ...)` and invokes the app's handler, which now believes the (attacker-controlled) payload legitimately originates from `victim-shop.myshopify.com`.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L12-22)
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
```
