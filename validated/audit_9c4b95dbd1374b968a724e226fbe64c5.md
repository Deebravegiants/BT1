### Title
Webhook `shop-domain` header is not covered by the HMAC signature, allowing cross-tenant shop spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by HMAC-verifying the raw request body, then trusts the unauthenticated `shop-domain` header to identify which tenant/shop the payload belongs to. Because the signature never covers the shop identity, the "shop that was cryptographically verified" and "shop that is acted upon" are two different values, breaking the required equality `verified_shop == acted_upon_shop`.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

while `shop`, `topic`, `webhook_id`, and `api_version` are all read directly from unauthenticated HTTP headers, independent of the signed payload: [2](#0-1) 

`Utils::HmacValidator.validate` computes the HMAC over `verifiable_query.to_signable_string` (i.e. body only) using the app's single, shop-independent `api_secret_key`, and compares it to the `hmac-sha256` header: [3](#0-2) 

`Registry.process` gates on that body-only HMAC check and then immediately builds `WebhookMetadata` using the caller-supplied, unverified `request.shop`: [4](#0-3) 

Because the same `api_secret_key` signs webhooks for *every* shop that installs the app, a valid `(raw_body, hmac)` pair generated for one shop remains cryptographically valid for any other shop identifier. An attacker who installs the public app on their own store (no special privilege required) automatically receives genuine, correctly-signed Shopify webhooks whose bodies they can shape by manipulating data in their own store before the webhook fires. The attacker can then replay that valid `(body, hmac)` pair to the app's public webhook endpoint while substituting an arbitrary `x-shopify-shop-domain` (or `shopify-shop-domain`) header value naming a victim shop. `Registry.process` will pass HMAC validation (the body is untouched) and will invoke the registered handler with `WebhookMetadata#shop` set to the attacker-chosen victim shop, causing the host application to process and persist attacker-controlled data as if it legitimately originated from the victim tenant.

This directly matches the "field acted on but not covered by the HMAC" bug class: the identity binding `hmac(payload) → shop` that the library's own documentation implies ("This will verify the request did indeed come from Shopify") does not actually hold, since only the body — not the shop — is authenticated.

### Impact Explanation
This is a cross-tenant confusion vulnerability: any unprivileged internet user capable of installing the target app on a shop they control can forge webhook deliveries attributed to a shop they do not control, with attacker-influenced body content. Depending on how the host application's webhook handler trusts `data.shop` (e.g., to key database writes, trigger fulfillment actions, redact/create records, or update per-shop state), this can lead to cross-tenant data corruption or unauthorized actions performed under another merchant's identity — squarely in the "cross-tenant access" impact category.

### Likelihood Explanation
Likelihood is meaningful but not trivial: the attacker must (1) be able to install the app on a shop of their choosing (satisfied for any publicly listed/embeddable app), (2) capture a legitimate webhook delivery for a chosen topic/body shape, and (3) be able to send arbitrary HTTP requests with custom headers to the app's public webhook callback URL, which is a documented, internet-reachable endpoint. No access token, `client_secret`, or privileged account is required.

### Recommendation
Bind the shop identity into the signature verification path rather than trusting it purely from headers:
- Include the `shop-domain` (and ideally `topic`/`webhook_id`) header value in the string that is HMAC-verified (`to_signable_string`), or
- Have host applications cross-check `request.shop` against the shop associated with the specific webhook registration/session before acting on the payload, and document this requirement clearly since the current library documentation overstates what `Registry.process` actually verifies.

### Proof of Concept
1. Attacker installs the target Shopify app on `attacker-shop.myshopify.com` (a store they control) and configures a webhook topic the app registers, e.g. `orders/create`.
2. Attacker triggers a real Shopify event so Shopify delivers a webhook `POST` to the app's callback path with body `B` and header `x-shopify-hmac-sha256: H`, where `H = HMAC-SHA256(api_secret_key, B)` — this is verifiable using the same logic in `ShopifyAPI::Utils::HmacValidator.validate_signature`: [5](#0-4) 
3. Attacker captures `(B, H)` and replays a new request to the same callback endpoint, keeping `B` and `H` identical, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which passes because the signature only ever validated `B`: [6](#0-5) 
5. The registered handler is invoked with `WebhookMetadata.new(... shop: request.shop ...)` where `request.shop == "victim-shop.myshopify.com"`, even though the payload actually originated from the attacker's own shop: [7](#0-6)

### Citations

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
