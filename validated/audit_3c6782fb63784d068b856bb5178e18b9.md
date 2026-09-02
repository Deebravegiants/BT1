### Title
Webhook `shop` identity is not covered by HMAC verification, enabling cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` verifies a webhook request by computing an HMAC over the raw body only, then blindly trusts the `x-shopify-shop-domain` (or `shopify-shop-domain`) header as the identity of the shop the payload belongs to. Because the shop header is never part of the signed content, an attacker who owns a legitimate installation of the target app (or otherwise obtains one genuinely-signed webhook payload+HMAC pair) can replay that exact body/HMAC pair while substituting an arbitrary `shop-domain` header, causing the app to process attacker-controlled webhook data under a victim shop's identity.

### Finding Description
`ShopifyAPI::Webhooks::Request` implements `Utils::VerifiableQuery`, and its `to_signable_string` returns only `@raw_body`: [1](#0-0) 

`shop` is read from a header that is completely independent of the signed content: [2](#0-1) 

`Utils::HmacValidator.validate` computes the HMAC exclusively over `verifiable_query.to_signable_string` (i.e., the raw body for webhooks) and compares it with `OpenSSL.secure_compare`: [3](#0-2) 

`Registry.process` validates the HMAC and then immediately hands `request.shop` to the app-provided handler as trusted tenant metadata, with no further check that this shop was ever registered or matches any known session: [4](#0-3) 

The identity binding that is broken is: `shop attested by Shopify's HMAC signature` ≠ `shop asserted by the unauthenticated x-shopify-shop-domain header consumed by the handler`. The library's own documentation reinforces the false assumption that the whole request is authenticated: "This will verify the request did indeed come from Shopify and then call the specified handler for that webhook," while also documenting `shop` as trusted webhook metadata ("`shop`, `String` - The shop domain of the webhook"): [5](#0-4) [6](#0-5) 

### Impact Explanation
An unprivileged internet user who has installed the app on their own store (or otherwise captured one valid webhook delivery) can capture a genuine `raw_body` + `hmac-sha256` pair that Shopify signed for their own shop. They can then POST that identical body and HMAC to the app's public webhook endpoint while forging the `x-shopify-shop-domain` header to name a different (victim) shop. `HmacValidator.validate` will succeed because it only checks the body, and the handler will receive `WebhookMetadata` claiming the payload belongs to the victim shop. Any app that keys data storage, redaction, order/customer creation, or other side effects off `data.shop` will attribute attacker-controlled data to the wrong tenant — a cross-tenant data-integrity/confidentiality violation (e.g. forging `customers/redact` or `shop/redact` mandatory webhooks against a shop the attacker doesn't control, or injecting fabricated `orders/create` data attributed to a victim shop).

### Likelihood Explanation
Exploitation requires only: (1) a public HTTP webhook endpoint, which is a normal, documented deployment configuration for every app using this gem, and (2) the attacker's own legitimate app installation on any shop (freely available to any unprivileged merchant/developer who installs a public app) to obtain one valid signed payload to replay with a modified header. No access to `api_secret_key` or any victim credential is required, matching the "no HMAC coverage of an acted-upon field" bug class directly.

### Recommendation
Bind the `shop` (and ideally `topic`/`webhook_id`) into the HMAC-covered signable content, or otherwise cryptographically tie the header-derived shop to the verified body (e.g., by having downstream consumers cross-check `data.shop` against a locally stored, previously-authenticated shop/session record before trusting it for any tenant-scoped side effect). At minimum, update `lib/shopify_api/webhooks/request.rb`/`registry.rb` and the documentation to make explicit that `shop-domain`, `topic`, and `webhook-id` headers are NOT authenticated by the HMAC check, so host applications don't treat `WebhookMetadata#shop` as a verified tenant identity.

### Proof of Concept
1. Attacker installs the vulnerable app on `attacker-shop.myshopify.com` and triggers a webhook (e.g. `orders/create`) to receive a real Shopify-signed delivery: `raw_body = B`, header `x-shopify-hmac-sha256 = H` (valid for `B` under the app's `api_secret_key`), `x-shopify-shop-domain: attacker-shop.myshopify.com`.
2. Attacker crafts a new POST to the app's public webhook endpoint reusing the exact same `raw_body = B` and `x-shopify-hmac-sha256 = H`, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
3. `Utils::HmacValidator.validate` recomputes the HMAC over `B` only (`Request#to_signable_string` returns `@raw_body`), matches `H`, and passes:
```ruby
raise Errors::InvalidWebhookError, "Invalid webhook HMAC." unless Utils::HmacValidator.validate(request)
```
4. `Registry.process` calls the registered handler with `WebhookMetadata.new(topic: ..., shop: "victim-shop.myshopify.com", body: JSON.parse(B), ...)`, causing the app to process attacker-supplied body content as if it originated from `victim-shop.myshopify.com`.

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

**File:** docs/usage/webhooks.md (L12-17)
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
