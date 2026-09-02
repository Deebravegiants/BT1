### Title
Webhook `shop-domain` (and topic/webhook-id) headers are trusted for tenant identification without being covered by the HMAC signature - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body, while `shop`, `topic`, `webhook_id`, and `api_version` are read directly from unauthenticated HTTP headers. `Registry.process` validates the HMAC over the body and, on success, forwards `request.shop` (the unsigned header value) to the app's handler as the tenant identifier. Since the header is not part of the signed data, an attacker who possesses one valid `(body, hmac)` pair can freely substitute the `shop-domain` header to impersonate a different tenant.

### Finding Description
`Utils::HmacValidator.validate` computes and compares the HMAC using only `verifiable_query.to_signable_string`: [1](#0-0) 

For webhooks, `to_signable_string` is defined as just the raw body: [2](#0-1) 

Meanwhile `shop`, `topic`, `webhook_id`, and `api_version` are all pulled straight from HTTP headers that are never included in the signable string: [3](#0-2) 

`Registry.process` validates only the body-derived HMAC and then trusts `request.shop` (an unsigned field) as the tenant identity when constructing the data passed to the app's handler: [4](#0-3) 

**Binding broken (equality that should hold but doesn't):**
`shop_bound_by_hmac == shop_delivered_to_handler`

In this gem, `shop_bound_by_hmac` is always empty (the signable string contains no shop field), while `shop_delivered_to_handler = request.shop` is taken from the unauthenticated `X-Shopify-Shop-Domain` / `shopify-shop-domain` header. The HMAC only proves "this body was signed with the app's secret for *some* shop", not "this body belongs to *this* shop."

### Impact Explanation
An unprivileged internet user who operates their own store with the app installed (or who otherwise obtains one legitimately-signed `(raw_body, hmac)` pair, e.g. by observing their own shop's webhook delivery) can replay that exact body/HMAC pair to the app's public webhook endpoint while substituting an arbitrary `shop-domain` header. `HmacValidator.validate` will still pass because the header is not part of the signed content, so `Registry.process` will call the registered handler with `WebhookMetadata#shop` set to the attacker-chosen victim shop domain. Any host application that uses this gem's `shop` field to key persistence, authorization, or business logic (the intended and documented use of `WebhookMetadata`) will process attacker-controlled webhook content under the identity of a different tenant, an actual cross-tenant confusion/write vector rather than a theoretical one.

### Likelihood Explanation
Exploitation requires no secrets beyond a single valid webhook delivery the attacker can obtain for their own store (trivial for anyone who installs the app), and webhook endpoints are, by design, public internet-facing endpoints. The only extra step is sending a crafted HTTP request with a substituted header, which is well within reach of an unprivileged internet user.

### Recommendation
Bind the shop (and ideally topic/webhook-id) into the signed payload verification instead of trusting headers post-hoc: include the shop-domain header value in `to_signable_string`, or independently verify that the `shop-domain` header matches metadata Shopify sends inside the signed body/registration where available, before using it as a tenant key in `WebhookMetadata`.

### Proof of Concept
1. Attacker installs the app on `attacker-shop.myshopify.com` and receives a legitimate webhook: `raw_body = B`, header `shopify-hmac-sha256 = H` (valid HMAC of `B` with the app's secret), header `shopify-shop-domain = attacker-shop.myshopify.com`.
2. Attacker replays the same request to the app's webhook endpoint but changes only the header: `shopify-shop-domain = victim-shop.myshopify.com`, keeping `raw_body = B` and `shopify-hmac-sha256 = H`.
3. `ShopifyAPI::Webhooks::Request.new(raw_body: B, headers: {..., "shopify-shop-domain" => "victim-shop.myshopify.com", "shopify-hmac-sha256" => H})` is constructed; `hmac` returns the decoded `H`.
4. `Registry.process(request)` calls `Utils::HmacValidator.validate(request)`, which recomputes HMAC over `B` only — it matches, since `B` and `H` are the untouched originals.
5. `handler.handle(data: WebhookMetadata.new(topic: ..., shop: "victim-shop.myshopify.com", body: JSON.parse(B), ...))` is invoked — the host app now processes attacker-controlled webhook content under the victim shop's identity.

### Citations

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
