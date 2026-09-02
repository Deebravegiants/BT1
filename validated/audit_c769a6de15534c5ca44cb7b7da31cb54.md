I have enough context to write up the finding now.

### Title
Webhook `shop` field is not covered by HMAC verification, allowing cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating the HMAC over the raw request body, then trusts the `X-Shopify-Shop-Domain` header verbatim and forwards it to the host application's handler as the identity of the shop that generated the event. The `shop` value is never included in the HMAC-signed payload, so the "authenticated" bytes (the body) and the "acted-upon" identity field (the shop) are not bound together.

### Finding Description
The equality that should hold is: `shop value cryptographically bound to the signed payload == shop value delivered to the handler`. In this gem that equality does not hold.

`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw body: [1](#0-0) 

The `shop` accessor simply reads the `shop-domain` header without any cryptographic binding: [2](#0-1) 

`Utils::HmacValidator.validate` computes the signature purely from `verifiable_query.to_signable_string` (i.e., the body) and compares it against the `hmac-sha256` header value: [3](#0-2) 

`Registry.process` treats a passing HMAC check as full authentication of the request, then immediately hands the unverified `request.shop` (along with `request.topic`, `request.api_version`, `request.webhook_id` — also unsigned) to the developer's handler via `WebhookMetadata`: [4](#0-3) 

`WebhookMetadata` carries `shop` as a plain, unauthenticated `String`: [5](#0-4) 

The library's own documentation reinforces the false assurance: it states that `Registry.process` "will verify the request did indeed come from Shopify," implying the whole request (including which shop it is for) is authenticated, when in fact only the raw body bytes are: [6](#0-5) 

Because the shop identity is not part of the signed material, any unprivileged internet user who can install the app on their own shop (a normal, unprivileged action) can capture a genuine, correctly-HMAC-signed webhook body/signature pair for their own shop, then replay that exact `raw_body` + `hmac-sha256` value to the app's webhook endpoint while substituting an arbitrary victim `X-Shopify-Shop-Domain` header. `HmacValidator.validate` will still succeed because it never inspects the shop header, and the host application's handler will process the payload as if it originated from the victim shop.

### Impact Explanation
This breaks the shop-authentication boundary between tenants: an attacker-controlled body is attributed to a shop that never sent it. Depending on how the host application keys its per-shop state (order records, inventory changes, deletion/refund handlers, GDPR/mandatory-webhook processors, uninstall handling, etc.) off `WebhookMetadata#shop`, this enables cross-tenant data corruption or disclosure — i.e., cross-tenant access, which the rules classify as Critical impact. This is caused entirely by this gem's own signature-computation and metadata-construction code (not by a host app ignoring documented behavior); the docs actively promise full request verification.

### Likelihood Explanation
Exploitation only requires an attacker to be able to install the target app on a shop they control (an unprivileged, normal onboarding action for any Shopify app) and to have an accessible webhook endpoint, both of which are standard conditions for any Shopify app. No access to `api_secret_key`, access tokens, or any privileged credential is required — the attacker reuses a legitimately-issued signature for different, forged metadata.

### Recommendation
Bind the shop identity to the authenticated payload before trusting it:
- Include the `shop-domain` (and ideally `topic`, `api-version`, `webhook-id`) header values in `to_signable_string`, or otherwise verify them cryptographically before use.
- Alternatively (and additionally, since Shopify's real signature only covers the body), require the host application to cross-check `request.shop` against a shop known to have the app installed (an existing offline session) before invoking the handler, and update the docs/`process` method to make clear that only the body — not the shop — is authenticated by the HMAC check.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com`, a normal unprivileged action.
2. Shopify sends a legitimate webhook to the app's endpoint with body `B`, header `X-Shopify-Shop-Domain: attacker-shop.myshopify.com`, and a correctly computed `X-Shopify-Hmac-Sha256: H = HMAC-SHA256(secret, B)`.
3. Attacker replays a request to the same endpoint with the identical body `B` and identical header `X-Shopify-Hmac-Sha256: H`, but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
4. `ShopifyAPI::Webhooks::Request.new` parses the forged headers; `Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes `HMAC-SHA256(secret, B)` and matches `H` — validation passes because `shop` is never part of the signed material (`lib/shopify_api/webhooks/request.rb:35-38`, `lib/shopify_api/utils/hmac_validator.rb:12-31`).
5. `Registry.process` invokes `handler.handle(data: WebhookMetadata.new(... shop: "victim-shop.myshopify.com" ...))` (`lib/shopify_api/webhooks/registry.rb:198-199`), causing the host application to process attacker-controlled data as belonging to `victim-shop.myshopify.com`.

### Citations

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

**File:** docs/usage/webhooks.md (L125-125)
```markdown
To process an http webhook, you need to listen on the route(s) you provided during the Webhook registration process, then when the route is hit construct a `ShopifyAPI::Webhooks::Request` and call `ShopifyAPI::Webhooks::Registry.process`. This will verify the request did indeed come from Shopify and then call the specified handler for that webhook. An example in Rails is shown below:
```
