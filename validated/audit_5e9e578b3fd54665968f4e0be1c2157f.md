### Title
Webhook shop attribution is not covered by the HMAC signature, allowing cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/webhooks/registry.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` treats a webhook as authentic once `Utils::HmacValidator.validate` succeeds, then hands the `shop` value straight from an HTTP header to the app's handler as trusted tenant identity. The HMAC, however, is only computed over the raw request body — never over the `shop-domain` header — so the "verified" request and the "acted-upon" shop identity are two different, independently-controllable things.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`shop` is read from an unauthenticated header (`shopify-shop-domain` / `x-shopify-shop-domain`) and is never included in the signable string: [2](#0-1) 

`HmacValidator.validate` only checks the `hmac` field against `to_signable_string`, i.e. the body, not headers such as `shop`: [3](#0-2) 

`Registry.process` accepts the request once that body-only HMAC check passes, and then forwards `request.shop` — the unverified header value — to the handler as the tenant identity for the event: [4](#0-3) 

The library's own documentation asserts that `process` "will verify the request did indeed come from Shopify," and describes `data.shop` to app authors as "The shop domain of the webhook," implying it is part of what was verified: [5](#0-4) [6](#0-5) 

This is exactly the "field acted on but not covered by the HMAC" identity-binding gap: the binding the code implicitly claims is `verified(request) == authentic(shop, body)`, but what is actually checked is only `verified(body)`. The `shop` field is free for anyone who can reach the app's public webhook endpoint to set, as long as they can pair it with *any* previously-observed valid `(body, hmac)` pair — which any merchant who has installed the app on their own store legitimately receives from Shopify for their own webhooks.

### Impact Explanation
An unprivileged internet user who has installed the target app on their own shop (any $0 developer/trial store qualifies) will receive real Shopify-delivered webhooks to the app's shared endpoint, each with a valid `hmac` for that specific body. Because `shop` is not part of the signed content, this same attacker can replay that exact `(topic, hmac, body)` triple to the app's endpoint while substituting an arbitrary `shop-domain` header naming a victim tenant. `HmacValidator.validate` still succeeds (body+hmac match), and `Registry.process` calls the app's handler with `data.shop` set to the attacker-chosen victim shop and `data.body` fully attacker-controlled (from their own tenant's legitimate webhook, and its content is otherwise attacker-influenced, e.g. product/order fields they set on their own store before the webhook fired). Any handler that keys persistence, authorization or business logic off `data.shop` (the documented, expected usage pattern) will apply attacker data to the victim shop's records — a cross-tenant data-integrity/confused-deputy issue.

### Likelihood Explanation
Likelihood is limited by needing "possession of one valid (body, hmac) pair for the app," which any user of the app (including a free/trial install) can trivially obtain by triggering a webhook on their own store and capturing the raw request Shopify sends. No secret material, session, or token is required — just internet access to the app's public webhook endpoint and a $0 shop.

### Recommendation
Bind the trusted shop identity into the value that is cryptographically verified. Concretely:
- Include the `shop-domain` header (and `topic`) inside `to_signable_string` in `lib/shopify_api/webhooks/request.rb` so the HMAC covers header+body, or
- Require the app to independently resolve `shop` from a value tied to registered webhook subscriptions rather than trusting the raw header, and document this requirement clearly instead of implying `process` fully authenticates `data.shop`.

### Proof of Concept
1. Install the target app (built on this gem) on attacker-owned dev shop `attacker.myshopify.com`.
2. Trigger a webhook (e.g. `products/update`) on `attacker.myshopify.com`; capture the raw POST Shopify sends to the app's webhook endpoint, including `X-Shopify-Hmac-Sha256: <hmac>` and body `{...}`.
3. Resend the identical body and `X-Shopify-Hmac-Sha256` value to the same endpoint, but replace `X-Shopify-Shop-Domain` with `victim-shop.myshopify.com`.
4. `ShopifyAPI::Utils::HmacValidator.validate` (`lib/shopify_api/utils/hmac_validator.rb:12-31`) returns `true` because it only checks the body against the HMAC.
5. `ShopifyAPI::Webhooks::Registry.process` (`lib/shopify_api/webhooks/registry.rb:188-200`) invokes the registered handler with `data.shop == "victim-shop.myshopify.com"` and `data.body` equal to the attacker's own product payload, even though `victim-shop` never sent this webhook.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L20-23)
```ruby
      sig { returns(String) }
      def shop
        T.cast(shopify_header("shop-domain"), String)
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

**File:** docs/usage/webhooks.md (L12-16)
```markdown
`data` will have the following keys
- `topic`, `String` - The topic of the webhook
- `shop`, `String` - The shop domain of the webhook
- `body`, `T::Hash[String, T.untyped]`- The body of the webhook
- `webhook_id`, `String` - The id of the webhook event to [avoid duplicates](https://shopify.dev/docs/apps/webhooks/best-practices#ignore-duplicates)
```

**File:** docs/usage/webhooks.md (L125-125)
```markdown
To process an http webhook, you need to listen on the route(s) you provided during the Webhook registration process, then when the route is hit construct a `ShopifyAPI::Webhooks::Request` and call `ShopifyAPI::Webhooks::Registry.process`. This will verify the request did indeed come from Shopify and then call the specified handler for that webhook. An example in Rails is shown below:
```
