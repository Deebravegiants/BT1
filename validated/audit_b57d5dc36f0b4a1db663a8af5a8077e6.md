### Title
Webhook `shop`, `topic`, and `webhook_id` are trusted from unsigned HTTP headers while the HMAC only covers the raw body - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` exposes `shop`, `topic`, `api_version`, and `webhook_id` by reading them straight out of HTTP headers, but the HMAC signature that `Utils::HmacValidator` checks is computed only over the raw request body. None of these header-derived identity fields are bound by the signature, so an attacker who possesses one validly-signed webhook body/HMAC pair (e.g. from their own, unprivileged app installation) can replay it against the same endpoint with a forged `shopify-shop-domain` header naming a different merchant, and the signature will still validate.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

Yet `shop`, `topic`, `api_version`, and `webhook_id` are all pulled from headers that are never mixed into that signable string: [2](#0-1) 

`HmacValidator.validate` computes `HMAC(secret, verifiable_query.to_signable_string)` and compares it to the `hmac` header — it never touches `shop`, `topic`, or `webhook_id`: [3](#0-2) 

`Registry.process` validates the HMAC and then immediately trusts `request.shop` and `request.topic` (unsigned) to route the payload and populate `WebhookMetadata`, which the host app's handler treats as the authenticated tenant/topic identity: [4](#0-3) 

The binding that should hold is:
`hmac_verified(raw_body) == true` **and** `shop_used_by_handler == shop_bound_by_hmac`

But what is actually enforced is only:
`HMAC(api_secret_key, raw_body) == received_hmac`, with `shop_used_by_handler = header["shopify-shop-domain"]` (attacker-controlled, unsigned).

Because a single app's `api_secret_key` is shared across every shop that installs the app, any attacker who operates their own (unprivileged) shop installation can capture a legitimately-signed webhook body+HMAC pair delivered to their own endpoint, then replay that exact body/HMAC to the same app endpoint while swapping the `shopify-shop-domain` (and/or `shopify-topic`, `shopify-webhook-id`) header to a victim shop. `HmacValidator.validate` still passes because it never inspects those headers, and `Registry.process` dispatches the (now falsely attributed) payload as if it originated from the victim shop/topic.

### Impact Explanation
This breaks the tenant-identity binding that the HMAC is supposed to provide: cross-tenant data can be injected into a host app's per-shop persistence/handler logic using only the attacker's own valid webhook traffic, without possessing the victim's data or any credentials belonging to the victim shop. This matches the Critical "cross-tenant access" category.

### Likelihood Explanation
Any entity that can install the target app on a shop they control (a routine, unprivileged, self-service action) can trigger a real webhook to capture a valid `raw_body` + `hmac`, then send a modified HTTP request with a swapped `shop-domain`/`topic`/`webhook-id` header to the same public webhook endpoint. No `api_secret_key`, access token, or victim credentials are needed — only observation of one's own legitimate webhook traffic, which is fully attacker-controlled.

### Recommendation
Bind `shop`, `topic`, and `webhook_id` into the value that is HMAC-verified (or otherwise cryptographically tie them to the signed body), for example by including them in `to_signable_string`, or by requiring the host app to independently confirm that the `shop-domain` header matches a shop with a known, previously-established session/installation before trusting `WebhookMetadata`.

### Proof of Concept
1. Install the app on attacker-controlled shop `attacker.myshopify.com`; trigger any subscribed webhook topic (e.g. `orders/create`) and capture the raw HTTP request, including `shopify-hmac-sha256` and body.
2. Resend the identical body and `shopify-hmac-sha256` header to the app's webhook endpoint, but replace `shopify-shop-domain` with `victim.myshopify.com` (and optionally change `shopify-topic`/`shopify-webhook-id`).
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which succeeds because it only checks `HMAC(api_secret_key, raw_body)`: [5](#0-4) 
4. The handler receives `WebhookMetadata` with `shop: "victim.myshopify.com"` even though the payload actually originated from `attacker.myshopify.com`, demonstrating the cross-tenant identity confusion.

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
