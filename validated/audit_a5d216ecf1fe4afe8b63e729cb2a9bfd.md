### Title
Webhook Tenant Identity (`shop`) Not Covered by HMAC Signature Allows Cross-Tenant Webhook Spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an incoming webhook solely by validating the HMAC over the raw request body, then trusts the `shop-domain` HTTP header — which is not part of the signed payload — as the tenant identity passed to the app's handler. Because the same `client_secret` is used to sign webhooks for every shop that has installed the app, an attacker who controls one shop where the app is installed can capture a genuinely-signed webhook and replay it with a forged `shop-domain` header pointing at a victim shop, causing the host application to process attacker-controlled data under another tenant's identity.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw body: [1](#0-0) 

The `shop`, `topic`, and `webhook_id` values are read directly from HTTP headers and are never included in the HMAC-signed string: [2](#0-1) 

`Registry.process` validates only the HMAC (which covers the body) and then forwards `request.shop` straight to the application's handler as the authenticated tenant: [3](#0-2) 

The equality the code implicitly assumes is:
`shop used to identify the tenant in WebhookMetadata == shop that produced the HMAC-signed body`

But this equality does not hold: the HMAC signature only proves "this body was signed with the app's `client_secret`" — it says nothing about which of the app's many installed shops produced it, because `client_secret` (and therefore the HMAC key) is shared across every shop installation of the app, per `HmacValidator.validate_signature` using `Context.api_secret_key`: [4](#0-3) 

Any shop owner that has legitimately installed the app can receive a real, validly-signed webhook for their own shop, then resend that exact HTTP request to the app's webhook endpoint while swapping the `X-Shopify-Shop-Domain` header to a victim shop's domain. The HMAC will still validate (body unchanged), but `WebhookMetadata.shop` will now falsely claim the victim shop as the source.

### Impact Explanation
This breaks the tenant boundary the library is supposed to help enforce. Host applications commonly use `WebhookMetadata#shop` from `Registry.process` as the authoritative tenant key to look up sessions, write data, or trigger tenant-scoped side effects. Since the shop field is unauthenticated relative to the signature, an unprivileged holder of one tenant's app installation can inject falsified events attributed to a different, victim tenant — a cross-tenant access primitive, which the rules classify as High impact.

### Likelihood Explanation
Exploitation requires only that the attacker install the app on their own store (a normal, unprivileged action available to any merchant/dev who can install a public or custom app), capture one webhook delivery, and replay it with a modified header value — no access to the app's `client_secret`, no leaked credentials, and no privileged account are required. This is a realistic, low-effort attack path reachable purely through this gem's own webhook-processing logic.

### Recommendation
Include the tenant-identifying fields (`shop`, `topic`, `webhook_id`) in the signed material used for HMAC verification, or otherwise cryptographically bind the `shop-domain` header to the signature (e.g., verify the shop against a known, previously-authenticated session/webhook registration rather than trusting the header verbatim). At minimum, document that `WebhookMetadata#shop` is not cryptographically authenticated and must not be used as a sole tenant-authorization signal.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com`, receiving genuine webhooks signed with the app's shared `client_secret`.
2. Attacker captures a legitimate webhook HTTP request (raw body + headers) sent to their own endpoint.
3. Attacker resends the identical raw body/HMAC to the app's webhook endpoint, but changes the `X-Shopify-Shop-Domain` header to `victim-shop.myshopify.com`.
4. `ShopifyAPI::Webhooks::Request.new` parses headers, `Registry.process` calls `HmacValidator.validate(request)`, which succeeds because it only hashes `@raw_body`: [1](#0-0) 
5. The handler receives `WebhookMetadata.new(shop: "victim-shop.myshopify.com", ...)`, and the host application processes/persists the attacker's payload as if it originated from the victim shop.

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
