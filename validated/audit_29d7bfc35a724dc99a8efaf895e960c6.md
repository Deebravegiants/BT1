### Title
Webhook HMAC signature does not cover the `shop-domain`, `topic`, or `webhook-id` headers, enabling cross-shop webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` derives `shop`, `topic`, `webhook_id`, and `api_version` from HTTP headers, but the HMAC signature that `ShopifyAPI::Webhooks::Registry.process` validates is computed only over the raw request body. Any actor who can obtain one genuinely-signed webhook (e.g. by installing the app on their own store) can replay that body/HMAC pair while forging the `shop-domain` (and `topic`/`webhook-id`) headers to impersonate any other shop, because none of those fields are bound to the signature.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Request#shop`, `#topic`, and `#webhook_id` are all read straight from attacker-controllable headers, independent of the signed body: [2](#0-1) 

`Utils::HmacValidator.validate` verifies only `verifiable_query.hmac` against `verifiable_query.to_signable_string` (the body), never the headers: [3](#0-2) 

`Registry.process` trusts `request.shop`/`request.topic` for dispatch after only validating the HMAC over the body, and forwards the header-derived `shop` value straight into the handler's metadata: [4](#0-3) 

Because the HMAC secret (`Context.api_secret_key`) is a single app-wide secret shared across every installed shop (not a per-shop secret), any user who installs the app on their own shop (e.g. a free development store) legitimately receives real webhooks with valid, correctly computed `hmac-sha256` values for that body. Since the signature never covers the `shop-domain` header, that same attacker can replay the identical `raw_body` + `hmac-sha256` pair to the app's public webhook endpoint while substituting a different `x-shopify-shop-domain` (and/or `topic`/`webhook-id`) value naming a victim shop. `HmacValidator.validate` still returns `true` because it only checks the body bytes, and `Registry.process` will hand the handler a `WebhookMetadata` claiming the payload originated from the victim shop.

This breaks the intended identity binding: **shop the HMAC actually authenticates == shop the handler believes it received data for**. Concretely: `bytes verified (raw_body) != fields acted on (shop-domain, topic, webhook-id headers)`.

### Impact Explanation
This allows cross-tenant confusion/spoofing: a handler that keys any state, side effects, or authorization decisions off `WebhookMetadata#shop` (as recommended by this library's own webhook usage docs) can be made to act on forged data attributed to a shop the attacker does not control, using only a webhook legitimately received on the attacker's own shop. This satisfies the "cross-tenant access" high/critical impact category since it lets an unprivileged user cause the app to process attacker-supplied data under another tenant's identity.

### Likelihood Explanation
Medium-to-high: the only prerequisite is that the attacker can install the target app on any shop they control (including a free Shopify partner/dev store) to receive one legitimately signed webhook, then replay it with modified headers to the app's public webhook endpoint. No access to `api_secret_key`, tokens, or victim credentials is required.

### Recommendation
Include the identity-bearing headers (`shop-domain`, `topic`, `webhook-id`, `api-version`) in the signable payload that is HMAC-verified, or otherwise cryptographically bind them to the body signature, so that a signature valid for one shop's webhook cannot be replayed with a different shop's identity attached.

### Proof of Concept
1. Attacker installs the target app on their own store `attacker-shop.myshopify.com` and receives a legitimate webhook for topic `orders/create` with body `B` and header `x-shopify-hmac-sha256: H`, where `H = HMAC-SHA256(client_secret, B)`.
2. Attacker POSTs to the app's webhook endpoint with the same raw body `B` and same header `x-shopify-hmac-sha256: H`, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes the HMAC over `B` only and matches `H`, so validation succeeds (`lib/shopify_api/utils/hmac_validator.rb` lines 12-31, `lib/shopify_api/webhooks/request.rb` lines 35-38).
4. The registered handler is invoked with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", topic: "orders/create", body: parsed(B), ...)` (`lib/shopify_api/webhooks/registry.rb` lines 188-200), even though the webhook never originated from `victim-shop`.

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
