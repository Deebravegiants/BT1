### Title
Webhook shop/topic/api-version/webhook-id headers are not covered by the HMAC signature, allowing cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb, lib/shopify_api/utils/hmac_validator.rb, lib/shopify_api/webhooks/registry.rb)

### Summary
`ShopifyAPI::Webhooks::Request` implements `Utils::VerifiableQuery#to_signable_string` by returning only the raw HTTP body, while `shop`, `topic`, `api_version`, and `webhook_id` are all read directly from unauthenticated HTTP headers. `HmacValidator.validate` only checks the HMAC over `to_signable_string` (the body), so none of these header-derived identity fields are cryptographically bound to the signature. `Webhooks::Registry.process` accepts a request as valid whenever the body HMAC matches, then constructs `WebhookMetadata` using the unverified `request.shop`, allowing an attacker who possesses one valid `(body, hmac)` pair to relabel it as belonging to a different shop.

### Finding Description
The HMAC validation binding is:

- HMAC is computed as `HMAC(api_secret_key, raw_body)` and compared against the `shopify-hmac-sha256` header via `OpenSSL.secure_compare`. [1](#0-0) 
- `Request#to_signable_string` returns only `@raw_body`, never the shop, topic, webhook id, or api version headers. [2](#0-1) 
- `Request#shop`, `#topic`, `#api_version`, `#webhook_id` are all read straight from request headers with no HMAC coverage. [3](#0-2) 
- `Registry.process` only gates on the body HMAC (`Utils::HmacValidator.validate(request)`), then immediately trusts `request.shop` and `request.topic` to build `WebhookMetadata`, which is what handler code uses to attribute the event to a tenant. [4](#0-3) 

The identity binding this breaks is: `shop authenticated (bytes actually covered by valid HMAC) != shop acted upon (header value passed to WebhookMetadata.shop)`. The `api_secret_key` used to sign webhooks is per-app, not per-shop — it is shared across every shop that installs the app. Consequently, if an attacker installs the app on shop A (or otherwise legitimately captures one valid `(raw_body, hmac)` pair for any topic on any shop using this app, since these are typically sent over plain HTTP endpoints controlled by the app developer, logged, proxied, or otherwise observable to an unprivileged actor who runs their own store on the same app), that attacker can replay the identical body and HMAC to the app's webhook endpoint while substituting the `shopify-shop-domain` header (and optionally `shopify-topic`/`shopify-webhook-id`) with a different target shop's domain. `HmacValidator.validate` still succeeds because it never looks at the headers, and `Registry.process` dispatches the handler with `WebhookMetadata.new(shop: request.shop, ...)` pointing at the attacker-chosen shop.

### Impact Explanation
This crosses a tenant boundary using only knowledge that is available to any unprivileged user of the multi-tenant app (their own captured webhook traffic), without needing the app's `client_secret`. Depending on what the host application does with `WebhookMetadata.shop` (e.g., updating/deleting records, disabling billing, revoking access, writing audit logs keyed by shop), this enables cross-tenant data corruption or spoofed events attributed to a victim shop — matching the "cross-tenant access" Critical impact class, since the trust boundary broken is exactly which tenant's data the payload is recorded against.

### Likelihood Explanation
Exploitation requires only: (1) being an installer of the same app on any shop (a normal unprivileged merchant), (2) capturing one legitimate webhook delivery for their own shop (trivial via a proxy/logging middleware they control, since it's delivered to their own endpoint), and (3) replaying the exact same body+HMAC with a modified `shop`/`topic` header to the target app's webhook endpoint. No secret material, TLS interception, or social engineering is required — this only depends on the fact that this library's own `to_signable_string`/`HmacValidator` never bind headers into the signed payload.

### Recommendation
Include the identity-critical headers (`shop-domain`, `topic`, and ideally `webhook-id`) in the signable string used for HMAC verification, or independently verify `request.shop` against a known/expected list of installed shops before trusting it in `WebhookMetadata`. At minimum, document in `Webhooks::Request`/`HmacValidator` that `shop`, `topic`, `webhook_id`, and `api_version` are NOT authenticated by the HMAC and host applications must not treat them as trusted tenant identifiers without additional verification.

### Proof of Concept
1. Attacker owns/operates `shop-a.myshopify.com`, which has the target app installed.
2. Attacker captures (or otherwise obtains, e.g. via their own request logs) one legitimate webhook delivery: `raw_body = B`, header `x-shopify-hmac-sha256 = H` (valid since `H = HMAC(api_secret_key, B)`), and `x-shopify-shop-domain: shop-a.myshopify.com`.
3. Attacker sends a new HTTP request to the app's webhook endpoint with the identical `raw_body = B` and `x-shopify-hmac-sha256: H`, but with `x-shopify-shop-domain: shop-victim.myshopify.com`.
4. `HmacValidator.validate` recomputes `HMAC(api_secret_key, B)` — using `Request#to_signable_string` which is only `B` — and it matches `H`, so validation passes: [5](#0-4) 
5. `Registry.process` dispatches the handler with `WebhookMetadata.new(shop: "shop-victim.myshopify.com", topic: ..., body: parsed(B), ...)`, so the app processes attacker-controlled body content attributed to `shop-victim`, even though the attacker never possessed `shop-victim`'s data or the app's secret for that shop specifically (the secret is shared across all shops anyway). [6](#0-5)

### Citations

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

**File:** lib/shopify_api/webhooks/request.rb (L15-38)
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

      sig { override.returns(String) }
      def to_signable_string
        @raw_body
      end
```

**File:** lib/shopify_api/webhooks/registry.rb (L189-200)
```ruby
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
