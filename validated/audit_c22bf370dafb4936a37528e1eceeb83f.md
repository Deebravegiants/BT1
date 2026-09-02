Confirmed root cause. The webhook `hmac` covers only the raw body via `to_signable_string` returning `@raw_body`, while `topic`, `shop`, `webhook_id`, and `api_version` are read straight from HTTP headers with no cryptographic binding to that signature.### Title
Webhook `shop` (and `topic`/`webhook-id`) identity not covered by HMAC signature — cross-tenant handler confusion - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw HTTP body, so `HmacValidator` cryptographically authenticates the payload bytes but never binds them to the `shop-domain`, `topic`, or `webhook-id` headers that `ShopifyAPI::Webhooks::Registry.process` uses to route and label the event. This mirrors the Sherlock M-5 report's root cause: a single check (the buffer/HMAC) is computed over one quantity, while a related but distinct value (the second flow / the routing headers) is used downstream without being independently validated, breaking an implicit identity binding.

### Finding Description
`Registry.process` validates the request purely on body+HMAC, then trusts the headers for tenant identity: [1](#0-0) 

`Request#hmac`/`#to_signable_string` show the signature is computed only over `@raw_body`: [2](#0-1) 

`Request#shop`, `#topic`, and `#webhook_id` are read straight from attacker-controllable headers with no cryptographic tie to the signed body: [3](#0-2) 

`HmacValidator.validate` confirms only that `hmac` matches `HMAC(secret, verifiable_query.to_signable_string)` — i.e. `HMAC(secret, raw_body)` — with no coverage of `shop`, `topic`, or `webhook_id`: [4](#0-3) 

The identity binding that should hold is:
`shop_header == shop_that_Shopify_actually_signed_this_body_for`

But since only `raw_body` is signed, the equality that is actually enforced is just:
`HMAC(secret, raw_body_received) == HMAC(secret, raw_body_expected)`

An unprivileged internet user who is a legitimate merchant installing the same multi-tenant app can trigger a genuine webhook delivery to the shared endpoint for their own store (e.g. `orders/create`), capture the valid `(raw_body, x-shopify-hmac-sha256)` pair, and resend it to the app's webhook endpoint with the `x-shopify-shop-domain` (and optionally `x-shopify-topic`/`x-shopify-webhook-id`) header swapped to point at a victim shop. `HmacValidator.validate` still succeeds because it only checks the untouched body against the signature, so `Registry.process` dispatches the handler with `WebhookMetadata.new(shop: request.shop, ...)` reporting the attacker-chosen victim shop, even though the body content actually belongs to the attacker's own store.

### Impact Explanation
This is a cross-tenant identity confusion: the app-level webhook handler (which typically uses `data.shop` to select/update the correct tenant's records) will process attacker-controlled body content under a victim shop's identity. Depending on how the host app uses this data (e.g., writing order/customer data keyed by `shop`), this can lead to cross-tenant data injection or corruption — matching the Critical "cross-tenant access" impact category in scope.

### Likelihood Explanation
No secret key, access token, or privileged account is required — only the ability to receive one legitimate webhook for the attacker's own installed shop (trivially achievable by any merchant using the app) and the ability to replay an HTTP request to the app's public webhook endpoint with a modified header. This is reachable entirely through the gem's own `Webhooks::Request`/`Registry` API as documented, with no reliance on the host app ignoring documented behavior — the gem itself never binds `shop`/`topic`/`webhook_id` to the signature.

### Recommendation
Include the identity-relevant headers (`shop-domain`, `topic`, `webhook-id`, `api-version`) in the signable string, or otherwise cryptographically bind them to the signed payload, so `HmacValidator.validate` fails if any of these headers are altered relative to what Shopify actually signed. At minimum, `to_signable_string` in `lib/shopify_api/webhooks/request.rb` should incorporate these header values rather than exclusively `@raw_body`.

### Proof of Concept
1. App installs on `attacker-shop.myshopify.com` and `victim-shop.myshopify.com` (same multi-tenant app instance/webhook endpoint).
2. Attacker triggers an event (e.g., creates an order) on their own store; Shopify sends a webhook to the shared endpoint with headers `x-shopify-shop-domain: attacker-shop.myshopify.com`, `x-shopify-hmac-sha256: <valid HMAC over raw_body>`, and the JSON body.
3. Attacker captures this exact `(raw_body, hmac)` pair (e.g., via their own request logging, browser devtools on a self-hosted proxy, or a load balancer they control in front of their own tunnel/test endpoint).
4. Attacker resends the identical `raw_body` and `x-shopify-hmac-sha256` to the app's webhook endpoint, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
5. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which passes because it only checks `raw_body` against the HMAC (`lib/shopify_api/utils/hmac_validator.rb:12-31`, `lib/shopify_api/webhooks/request.rb:36-38`).
6. The handler is invoked with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", body: <attacker's order data>, ...)` (`lib/shopify_api/webhooks/registry.rb:198-199`), causing the app to process attacker-controlled data under the victim's tenant identity.

### Citations

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

**File:** lib/shopify_api/webhooks/request.rb (L10-38)
```ruby
      sig { override.returns(String) }
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
      end

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
