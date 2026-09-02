This confirms the vulnerability path. The `HmacValidator` computes the signature only over `Request#to_signable_string`, which returns `@raw_body` alone.This confirms the root cause: `HmacValidator.validate` at `lib/shopify_api/utils/hmac_validator.rb:12-22` computes and compares the HMAC solely against `verifiable_query.to_signable_string`, and for webhooks that method — `Request#to_signable_string` at `lib/shopify_api/webhooks/request.rb:35-38` — returns only `@raw_body`. The `shop`, `topic`, `api_version`, and `webhook_id` values used by `Registry.process` (`lib/shopify_api/webhooks/registry.rb:188-199`) come from HTTP headers (`Request#shop`, `lib/shopify_api/webhooks/request.rb:20-23`) that are never included in the signed bytes, so any header can be swapped without invalidating the signature, breaking the binding `hmac(raw_body) == authenticated(shop)`.

### Title
Webhook shop-domain identity not bound to HMAC signature, enabling cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` derives `shop` (and `topic`, `api_version`, `webhook_id`) purely from HTTP headers, while `to_signable_string` — the value that `Utils::HmacValidator` verifies against the `X-Shopify-Hmac-Sha256` header — is only the raw request body. The HMAC therefore authenticates the payload's integrity but never binds it to the sender's shop identity that the handler subsequently trusts.

### Finding Description
`Registry.process` performs a single check before dispatching to the app's handler: [1](#0-0) 
It calls `Utils::HmacValidator.validate(request)`, which computes `HMAC-SHA256(secret, verifiable_query.to_signable_string)` and compares it to the `hmac` supplied by the caller: [2](#0-1) 
For `Webhooks::Request`, `to_signable_string` returns only `@raw_body`: [3](#0-2) 
Meanwhile `shop`, `topic`, `api_version`, and `webhook_id` are read straight from caller-supplied HTTP headers with no cryptographic tie to the body or hmac: [4](#0-3) 
`Registry.process` then forwards `request.shop` directly into `WebhookMetadata`, which the app's handler is documented to trust as the tenant identifier for the event: [5](#0-4) [6](#0-5) 

The equality the app relies on is `hmac_valid(raw_body) == authenticated(shop_header)`. In reality only `raw_body` is signed; `shop_header` is unauthenticated attacker-controlled input at the transport layer (the app's own HTTP endpoint receives arbitrary headers from whoever posts to it — this is the same "field acted on but not covered by the signature" defect class as the reported unchecked-transfer bug, here applied to the identity-binding header instead of a return value).

### Impact Explanation
Because the app's client secret (used to compute the webhook HMAC) is identical for every shop that installs the app, a merchant who legitimately installs the app can trigger a genuine Shopify webhook delivery for their own store, capture the resulting valid `(raw_body, hmac)` pair, then replay that exact body/hmac to the app's public webhook endpoint while substituting the `X-Shopify-Shop-Domain` (and/or `X-Shopify-Topic`/`X-Shopify-Webhook-Id`) header for a different, unrelated shop. `HmacValidator.validate` still returns `true` because it never inspected those headers, and `Registry.process` hands the forged `shop` value straight to the app's handler, which — per the documented usage pattern — persists or acts on data keyed by that shop. This allows cross-tenant data injection/corruption (e.g., writing another merchant's order/customer data, or the mandatory `shop/redact`/`customers/redact` compliance topics) without ever possessing that other shop's credentials.

### Likelihood Explanation
Any user able to install the app on a shop they control can obtain a validly signed webhook body/hmac pair for that shop (webhooks are delivered to a public HTTPS endpoint the attacker can also reach directly with a raw HTTP client), and no additional secret is needed to forge the header values that determine tenant attribution downstream. This requires no access to `api_secret_key`, no leaked credentials, and no privileged account beyond a normal, self-service app installation.

### Recommendation
Include the shop domain (and ideally topic/webhook id) inside the signed material, or otherwise cryptographically bind the header-derived `shop` to the verified payload before trusting it — e.g., have `Request#to_signable_string` incorporate the shop header, or require handlers/`Registry.process` to cross-check the resolved shop against session/subscription state registered for that specific `webhook_id` (fetched from Shopify, not trusted from the header) before dispatching.

### Proof of Concept
1. Install the target app on attacker-owned shop `attacker.myshopify.com`; trigger any subscribed webhook (e.g. `orders/create`) so Shopify delivers a POST with a valid `X-Shopify-Hmac-Sha256` for that `raw_body`.
2. Capture `raw_body` and the `X-Shopify-Hmac-Sha256` header value from that delivery.
3. Send a new POST directly to the app's public webhook endpoint with the identical `raw_body` and `X-Shopify-Hmac-Sha256`, but set `X-Shopify-Shop-Domain: victim.myshopify.com` (a shop the attacker does not control).
4. `ShopifyAPI::Utils::HmacValidator.validate` (`lib/shopify_api/utils/hmac_validator.rb:12-22`) returns `true` because only `raw_body` was checked; `Registry.process` (`lib/shopify_api/webhooks/registry.rb:188-199`) dispatches `WebhookMetadata` with `shop: "victim.myshopify.com"` to the app's handler, which processes/persists the attacker's data under the victim's tenant.

### Citations

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

**File:** lib/shopify_api/webhooks/request.rb (L35-38)
```ruby
      sig { override.returns(String) }
      def to_signable_string
        @raw_body
      end
```

**File:** docs/usage/webhooks.md (L10-17)
```markdown
If you want to register for an http webhook you need to implement a webhook handler which the `shopify_api` gem can use to determine how to process your webhook. You can make multiple implementations (one per topic) or you can make one implementation capable of handling all the topics you want to subscribe to. To do this simply make a module or class that includes or extends `ShopifyAPI::Webhooks::WebhookHandler` and implement the `handle` method which accepts the following named parameters: data: `WebhookMetadata`. An example implementation is shown below:

`data` will have the following keys
- `topic`, `String` - The topic of the webhook
- `shop`, `String` - The shop domain of the webhook
- `body`, `T::Hash[String, T.untyped]`- The body of the webhook
- `webhook_id`, `String` - The id of the webhook event to [avoid duplicates](https://shopify.dev/docs/apps/webhooks/best-practices#ignore-duplicates)
- `api_version`, `String` - The api version of the webhook
```
