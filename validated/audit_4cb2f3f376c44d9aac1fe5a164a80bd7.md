### Title
Webhook `shop` field is not covered by the HMAC signature, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` validates a webhook exclusively over the raw request body, but hands the caller a `shop` value that comes from an unauthenticated HTTP header. Any entity capable of obtaining one genuine, HMAC-valid webhook (e.g., a merchant who has legitimately installed the app) can replay that exact body/HMAC pair while substituting the `shop-domain` header for an arbitrary victim shop, and the library will report the request as verified and hand the forged shop identity to the app's business logic.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`ShopifyAPI::Utils::HmacValidator.validate` computes/verifies the signature purely from that signable string against the single, app-wide `Context.api_secret_key`: [2](#0-1) 

`Registry.process` treats a passing HMAC check as proof the whole request — including the shop identity — is authentic, then forwards `request.shop` (sourced from the `shopify-shop-domain`/`x-shopify-shop-domain` header, which is never part of the signed bytes) straight to the app's handler as the tenant identifier: [3](#0-2) [4](#0-3) 

The documentation reinforces that this is the library's guaranteed contract, not a caller responsibility: `process` "will verify the request did indeed come from Shopify," and `data.shop` is described simply as "The shop domain of the webhook" with no caveat that it must be independently re-verified by the host app: [5](#0-4) [6](#0-5) 

The equality being broken is: `shop asserted by the (unauthenticated) header` ≠ `shop actually bound by the cryptographic proof (the body only)`. Because `api_secret_key` is the app's single shared secret and is identical for webhooks generated for *every* installed shop (not shop-specific), any shop that installs the app can capture a body+HMAC pair that is valid against that shared secret, then resend it with a different `shop-domain` header value naming a different, victim shop. `HmacValidator.validate` will still return `true` because it never inspects the header, and `Registry.process` will dispatch to the handler with `shop` set to the attacker-chosen value.

### Impact Explanation
This crosses the tenant boundary the gem is supposed to enforce: an unprivileged app user (any merchant who installs the app, no elevated credentials or `api_secret_key` needed) can make the host application believe a webhook body originated from a shop it does not control. Any host logic that uses `data.shop` to key data writes, enqueue per-shop jobs, or trigger and store account/subscription-affecting events for "the shop" will act on a spoofed tenant — a cross-tenant access impact.

### Likelihood Explanation
Likelihood is high in any app that registers webhooks: obtaining one legitimately signed body/HMAC pair only requires installing the app in the attacker's own shop (something any user can do), and replaying it with a modified header is a trivial HTTP replay with no cryptography to break.

### Recommendation
Bind the `shop` (and ideally `webhook_id`/`topic`) into the value that is cryptographically verified — e.g., include the shop domain in the signable string that is HMAC-checked, or require the caller to supply/verify the shop against the app's known installed-shops list before trusting `WebhookMetadata#shop`, and document this requirement explicitly if the header cannot be brought inside the HMAC scope for backward-compatibility reasons.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com`, triggering a real webhook. Shopify computes `hmac = HMAC-SHA256(api_secret_key, raw_body)` and sends it with header `x-shopify-shop-domain: attacker-shop.myshopify.com`.
2. Attacker captures `raw_body` and `hmac` (both are exposed in the webhook POST they receive on their own server).
3. Attacker resends the identical `raw_body` and `hmac` to the app's webhook endpoint, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which only checks `raw_body` against `hmac` — this passes because both are byte-for-byte identical to the original legitimate request.
5. `process` then invokes the registered handler with `WebhookMetadata.new(topic:, shop: "victim-shop.myshopify.com", body:, ...)`, causing the host app to process attacker-supplied data under the victim shop's identity.

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

**File:** docs/usage/webhooks.md (L12-17)
```markdown
`data` will have the following keys
- `topic`, `String` - The topic of the webhook
- `shop`, `String` - The shop domain of the webhook
- `body`, `T::Hash[String, T.untyped]`- The body of the webhook
- `webhook_id`, `String` - The id of the webhook event to [avoid duplicates](https://shopify.dev/docs/apps/webhooks/best-practices#ignore-duplicates)
- `api_version`, `String` - The api version of the webhook
```

**File:** docs/usage/webhooks.md (L123-125)
```markdown
## Process a Webhook

To process an http webhook, you need to listen on the route(s) you provided during the Webhook registration process, then when the route is hit construct a `ShopifyAPI::Webhooks::Request` and call `ShopifyAPI::Webhooks::Registry.process`. This will verify the request did indeed come from Shopify and then call the specified handler for that webhook. An example in Rails is shown below:
```
