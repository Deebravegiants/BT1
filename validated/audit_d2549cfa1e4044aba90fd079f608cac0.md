This finding confirms the vulnerability: the gem's docs explicitly claim `Registry.process` "will verify the request did indeed come from Shopify" [1](#0-0) , and hands `data.shop` to the app's handler as trusted identity [2](#0-1) , but the `shop` field is never covered by the HMAC signature.

### Title
Webhook `shop-domain` identity is not bound by HMAC, enabling cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body, and `ShopifyAPI::Utils::HmacValidator.validate` verifies the HMAC over that signable string alone. The `shop` (and `topic`, `webhook_id`, `api_version`) values are read from unauthenticated HTTP headers and are never included in the HMAC computation, yet they are trusted and forwarded to the app's handler as the webhook's origin.

### Finding Description
`Request#to_signable_string` is defined as: [3](#0-2) 

`shop` is read straight from a header with no cryptographic binding to the HMAC: [4](#0-3) 

`Registry.process` validates only the HMAC (which covers the body, not the `shop` header) and then dispatches to the handler using `request.shop`, which becomes `WebhookMetadata#shop`: [5](#0-4) 

The equality this breaks: the binding should be `hmac == HMAC(secret, body ∥ shop)` (or equivalent), but the gem only checks `hmac == HMAC(secret, body)`. All shops installed on a given app share the same `Context.api_secret_key` (a single app-wide secret, not per-shop), since `HmacValidator.validate` always signs with the single configured `Context.api_secret_key`: [6](#0-5) 

Because the same secret signs webhooks for every merchant shop on the app, and the signature never covers `shop`, a valid `(body, hmac)` pair legitimately obtained for one shop (e.g. an attacker's own install of the app) remains valid when replayed with the `x-shopify-shop-domain`/`shopify-shop-domain` header changed to a victim shop. `Registry.process` will accept it as authentic and hand the attacker-chosen `shop` value to the app's handler as trusted data.

### Impact Explanation
This is a cross-tenant identity-binding break: an unprivileged user who legitimately installs the app on their own shop can forge/replay webhook payloads that are attributed to a different, victim merchant's shop. Any host application that keys business logic (e.g., order processing, inventory updates, data attribution) off `data.shop` as documented — "will verify the request did indeed come from Shopify" — is exposed to cross-tenant data injection/confusion, since the gem's own verification never authenticates the shop identity, only the body bytes.

### Likelihood Explanation
Requires no access to `api_secret_key`, access tokens, or any privileged credential — only that the attacker be a legitimate merchant/installer of the target app (an "unprivileged internet user" relative to any other tenant), and can send an arbitrary HTTP POST to the app's public webhook endpoint with a modified `shop` header and a body they already have a valid signature for (e.g., a fixed/predictable body such as `{}` or a replayed payload from their own shop).

### Recommendation
Include the `shop` (and ideally `topic`/`webhook_id`) values in the HMAC-signed material, or independently verify that the `shop` header corresponds to a shop with an active, stored session/installation before trusting `request.shop` in `Registry.process`, rather than relying solely on body-only HMAC validation.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com`, receiving genuine webhooks signed with the app's shared `api_secret_key`.
2. Attacker captures one such webhook: raw body `B` and header `x-shopify-hmac-sha256: H`, where `H = HMAC-SHA256(api_secret_key, B)` — this is valid because `Request#to_signable_string` only returns `@raw_body` [3](#0-2) .
3. Attacker POSTs the same body `B` and same `H` to the app's webhook endpoint but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes `HMAC(api_secret_key, B)` and matches `H` [7](#0-6) , since `shop` is not part of the signed content.
5. The handler is invoked with `WebhookMetadata.new(... shop: "victim-shop.myshopify.com", ...)` [8](#0-7) , causing the host app to process attacker-controlled data as if it originated from the victim shop.

### Citations

**File:** docs/usage/webhooks.md (L12-18)
```markdown
`data` will have the following keys
- `topic`, `String` - The topic of the webhook
- `shop`, `String` - The shop domain of the webhook
- `body`, `T::Hash[String, T.untyped]`- The body of the webhook
- `webhook_id`, `String` - The id of the webhook event to [avoid duplicates](https://shopify.dev/docs/apps/webhooks/best-practices#ignore-duplicates)
- `api_version`, `String` - The api version of the webhook

```

**File:** docs/usage/webhooks.md (L125-125)
```markdown
To process an http webhook, you need to listen on the route(s) you provided during the Webhook registration process, then when the route is hit construct a `ShopifyAPI::Webhooks::Request` and call `ShopifyAPI::Webhooks::Registry.process`. This will verify the request did indeed come from Shopify and then call the specified handler for that webhook. An example in Rails is shown below:
```

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

**File:** lib/shopify_api/webhooks/registry.rb (L189-199)
```ruby
        def process(request)
          raise Errors::InvalidWebhookError, "Invalid webhook HMAC." unless Utils::HmacValidator.validate(request)

          handler = @registry[request.topic]&.handler

          unless handler
            raise Errors::NoWebhookHandler, "No webhook handler found for topic: #{request.topic}."
          end

          handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop,
            body: request.parsed_body, api_version: request.api_version, webhook_id: request.webhook_id))
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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```
