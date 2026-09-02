### Title
Webhook `shop`/`topic` identity fields are not covered by the HMAC signature, enabling cross-tenant webhook spoofing - (`lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/webhooks/registry.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` treats a webhook request as fully authenticated once `Utils::HmacValidator.validate` succeeds, but that HMAC only ever covers the JSON body bytes, not the `shop-domain` or `topic` headers that the registry actually acts on when dispatching the webhook to a handler.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`HmacValidator.validate` computes the signature strictly from `to_signable_string`, i.e. the body only: [2](#0-1) 

`Registry.process` accepts the request once that body-only HMAC check passes, and then dispatches using `request.shop` and `request.topic`, both of which come straight from unauthenticated headers: [3](#0-2) [4](#0-3) 

The `api_secret_key` used to compute the HMAC is the app's single shared client secret (not per-shop), applied identically for every shop the app serves: [5](#0-4) 

This is the same class of bug as the analog report: a value that is *acted on* (the tenant-identifying `shop` and the `topic`, used to route/dispatch data to the handler) is not covered by the cryptographic binding (`hmac` over `raw_body` only), so it can be swapped independently of the signed bytes without invalidating the signature — exactly like `endSqrtPrice` being allowed to diverge from the range the TWA is computed against.

The equality that should hold is: `hmac_valid(raw_body) == true` should imply `shop_used_for_dispatch == shop_that_actually_sent_this_body`. In this gem, `hmac_valid(raw_body)` is independent of `shop`/`topic`, so that equality does not hold — an attacker can present the same signed body with a different `shop-domain`/`topic` header and it will still validate.

The library's own documentation reinforces the false assumption that header-derived fields are authenticated: "This will verify the request did indeed come from Shopify and then call the specified handler for that webhook," with no caveat that `shop`/`topic` are unauthenticated: [6](#0-5) 

### Impact Explanation
Because the HMAC is keyed by the single app-wide `api_secret_key` and only covers the body, any legitimate webhook body/HMAC pair captured for one shop remains valid when replayed with a forged `shop-domain` header pointing at a different shop, or a different `topic` header. A handler implementation that trusts `WebhookMetadata#shop`/`#topic` (as the documented usage pattern explicitly instructs) can be made to process attacker-chosen body content under a victim shop's identity — a cross-tenant confusion at the point where this gem hands data to the app. This matches the Critical "cross-tenant access" impact category.

### Likelihood Explanation
Exploitation requires only the ability to trigger one legitimate webhook delivery for any shop under the same app (e.g., an unprivileged merchant/customer causing an `orders/create` event on their own store) to obtain a body+valid-HMAC pair, then replaying it to the app's public webhook endpoint with modified `shopify-shop-domain`/`shopify-topic` headers. No access token, `api_secret_key`, or privileged account is needed — the gem itself performs the "verification" and hands the spoofed identity fields straight to the handler.

### Recommendation
Include `shop`, `topic`, and `webhook_id` in the signable content used for HMAC verification (or otherwise cryptographically bind them, e.g. by re-deriving/whitelisting the expected shop/topic pair server-side against the shop that originally registered the webhook) instead of relying solely on the raw body for `Utils::HmacValidator.validate`. At minimum, update `docs/usage/webhooks.md` to clearly state that `shop`/`topic` are not covered by the HMAC and must be independently verified by the app before being trusted as the tenant identity.

### Proof of Concept
1. App is installed on `shop-a.myshopify.com` and `shop-b.myshopify.com` (both use the same `api_secret_key`).
2. Trigger a legitimate webhook for `shop-a` (e.g., create an order), capturing `raw_body` and the resulting `x-shopify-hmac-sha256` header — this HMAC is valid because it's computed only from `raw_body` with the shared secret: [7](#0-6) 
3. Replay this exact `raw_body` + `hmac` to the app's webhook endpoint, but with `x-shopify-shop-domain: shop-b.myshopify.com` (and/or a different `x-shopify-topic`).
4. `HmacValidator.validate` succeeds (it only checks `raw_body`): [8](#0-7) 
5. `Registry.process` dispatches the handler with `WebhookMetadata.new(topic: request.topic, shop: request.shop, ...)`, so the app's handler processes shop-a's data believing it belongs to shop-b: [9](#0-8)

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-13)
```ruby
      sig { override.returns(String) }
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
      end
```

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

**File:** docs/usage/webhooks.md (L125-125)
```markdown
To process an http webhook, you need to listen on the route(s) you provided during the Webhook registration process, then when the route is hit construct a `ShopifyAPI::Webhooks::Request` and call `ShopifyAPI::Webhooks::Registry.process`. This will verify the request did indeed come from Shopify and then call the specified handler for that webhook. An example in Rails is shown below:
```
