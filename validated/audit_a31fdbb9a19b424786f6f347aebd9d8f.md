### Title
Webhook HMAC only signs the raw body; the shop-domain (and other Shopify-\* headers) used to attribute the event are unauthenticated, enabling cross-tenant webhook forgery - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` derives the `shop` (and `topic`, `webhook_id`, `api_version`) that get handed to the app's webhook handler from HTTP headers, but `Utils::HmacValidator` only verifies the raw request body against the HMAC. The header that identifies *which tenant* the event belongs to is never covered by the signature, so any party who can obtain one valid `(body, hmac)` pair can replay it against the app's public webhook endpoint with an arbitrary `shop-domain` header and have the app process attacker-controlled content as if it originated from a victim shop.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

but `shop`, `topic`, `webhook_id`, and `api_version` are all read straight from HTTP headers that are not part of that signable string: [2](#0-1) 

`Registry.process` validates the request purely via `Utils::HmacValidator.validate(request)`, which computes the HMAC over `to_signable_string` (i.e. only the body bytes) and compares it to the `hmac-sha256` header: [3](#0-2) [4](#0-3) 

The `shop` value that passes the HMAC check is then handed directly to the app's `WebhookHandler` as the tenant identifier (`WebhookMetadata.shop`), and this is the documented, canonical way apps determine which shop a webhook belongs to: [5](#0-4) 

The identity binding that should hold is: `shop that produced the HMAC-verified bytes == shop the app attributes the event to`. Because the signature covers only `raw_body` and not the `shop-domain` header, this equality is not enforced by the library — the header can be swapped after the fact without invalidating the signature.

### Impact Explanation
Any party capable of obtaining one legitimately-signed `(body, hmac)` pair for the shared app secret (e.g. by installing the app on their own store, or receiving any webhook Shopify sends to that endpoint) can replay that exact payload to the app's public webhook endpoint while substituting the `X-Shopify-Shop-Domain` (and/or `X-Shopify-Topic`, `X-Shopify-Webhook-Id`) header to name a victim shop. `HmacValidator.validate` still returns `true` because it only checks the untouched body bytes, and `Registry.process` calls the app's handler with `shop: <victim shop>` and attacker-controlled `body`. Since apps are expected to key persisted data, uninstall/GDPR actions, and other tenant-scoped side effects off `data.shop` (per the gem's own documented usage pattern), this allows cross-tenant data injection/corruption or spoofed lifecycle events (e.g. spoofed `app/uninstalled`, `shop/redact`, `customers/redact`) attributed to a shop the attacker does not own — a cross-tenant access vulnerability.

### Likelihood Explanation
The webhook endpoint is, by design, a public HTTP endpoint reachable by anyone (Shopify calls it over the internet), so no privileged access to the app is required to send the forged request. Obtaining a valid `(body, hmac)` pair only requires becoming a legitimate installer of the target app on any shop (a normal, unprivileged action for public/multi-tenant apps) and capturing one webhook Shopify sends for that installer's own shop — no access to `api_secret_key` is needed. The replay technique itself (swap one header, keep body/hmac unchanged) requires no cryptographic effort.

### Recommendation
Include the tenant-identifying headers (`shop-domain`, and ideally `topic`/`webhook_id`/`api_version`) in the HMAC-covered signable string, or otherwise cryptographically bind them to the verified body (e.g. Shopify already signs the body per-request; the library should not trust unsigned headers as the source of truth for tenant attribution). At minimum, document that consuming apps must independently corroborate `data.shop` against a shop they have an active, valid session/installation for, and reject header-derived shop values that aren't otherwise verified.

### Proof of Concept
1. Attacker installs the vulnerable app on their own store `attacker.myshopify.com` and lets Shopify deliver a legitimate webhook (e.g. `orders/create`) to the app's public endpoint. Attacker captures the request: `raw_body = B`, header `X-Shopify-Hmac-Sha256 = H` (valid HMAC of `B` under the app's shared secret), `X-Shopify-Shop-Domain: attacker.myshopify.com`.
2. Attacker resends the identical `body = B` and `X-Shopify-Hmac-Sha256: H` to the same endpoint, but sets `X-Shopify-Shop-Domain: victim.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new(raw_body: B, headers: {...shop-domain: "victim.myshopify.com", hmac-sha256: H...})` is constructed; `Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes HMAC over `B` only and matches `H` → validation succeeds.
4. The registered handler is invoked with `WebhookMetadata.shop == "victim.myshopify.com"` and attacker-controlled `body`, even though `victim.myshopify.com` never sent this webhook — demonstrating the cross-tenant identity-binding break.

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
