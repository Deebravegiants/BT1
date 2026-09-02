### Title
Webhook shop-domain identity not bound to HMAC allows cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary

### Finding Description
The gem's webhook signature verification computes the HMAC only over the raw request body, never over the `shop` (tenant identity) that the app subsequently trusts. `Webhooks::Request#to_signable_string` returns just `@raw_body` [1](#0-0) , while `shop` is read independently from the unauthenticated `shopify-shop-domain`/`x-shopify-shop-domain` header [2](#0-1) . `Registry.process` validates only `Utils::HmacValidator.validate(request)` and then forwards `request.shop` straight into `WebhookMetadata`, which the app's handler uses as the tenant identifier [3](#0-2) . `HmacValidator.validate_signature` computes `HMAC(secret, verifiable_query.to_signable_string)` and compares it to the received signature [4](#0-3) ; since `to_signable_string` is only the body, the signature never binds to `shop`.

Critically, the HMAC secret (`Context.api_secret_key`) is the app's single, global `client_secret` — it is **not** a per-shop secret, it is shared across every shop that has installed the app [5](#0-4) . `WebhookMetadata.shop` is defined as the trusted tenant field passed to `WebhookHandler#handle` [6](#0-5) .

The equality that should hold but doesn't:
`bytes_covered_by_HMAC == identity_field_trusted_by_handler`
Here `bytes_covered_by_HMAC = raw_body` while `identity_field_trusted_by_handler = shop header`, so they are disjoint.

### Impact Explanation
Because the same `api_secret_key` is used to compute a valid HMAC for *any* shop's webhook body, an unprivileged attacker who legitimately installs the app on their own store (a normal, non-privileged action available to anyone) will receive real webhooks with a correctly computed HMAC over the body. The attacker can capture one such `(raw_body, hmac)` pair from their own shop and resend it directly to the app's public webhook endpoint while substituting the `x-shopify-shop-domain` header with a victim shop's domain. `HmacValidator.validate` will still pass (it only checks the body/secret, never the shop), and `Registry.process` will hand the handler a `WebhookMetadata` claiming the payload originated from the victim shop [7](#0-6) . Any app that uses `data.shop` to select which tenant's record to create/update/delete (the documented and intended use of this field) can be tricked into applying attacker-controlled data to a different merchant's tenant — a cross-tenant integrity/confidentiality violation.

### Likelihood Explanation
Requires only: (1) attacker installs the app on any shop (unprivileged, self-service action for any Shopify merchant/developer testing an app), (2) attacker sends a crafted POST to the app's public webhook callback URL with a swapped `shop-domain` header. No access token, no `client_secret`, no privileged account, and no interception of TLS is needed — only observation of the attacker's own legitimately delivered webhook traffic.

### Recommendation
Bind the tenant identity into the signed material or otherwise independently authenticate it — e.g., include the `shop` domain in the HMAC-covered signable string (analogous to how `Auth::Oauth::AuthQuery#to_signable_string` folds `shop` into the signed query [8](#0-7) ), or require the caller to cross-check `request.shop` against an expected/registered shop domain before trusting it, rather than accepting any header-supplied shop paired with a body-only HMAC.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com` and registers an HTTP webhook handler is invoked normally; Shopify sends:
   - Headers: `x-shopify-topic: orders/create`, `x-shopify-shop-domain: attacker-shop.myshopify.com`, `x-shopify-hmac-sha256: <valid HMAC of BODY under shared api_secret_key>`
   - Body: `BODY` (attacker fully controls the order content within Shopify's own limits, or can encode arbitrary JSON they crafted resembling a real payload if resent via replay of an actual delivery)
2. Attacker resends the exact same `BODY` and `x-shopify-hmac-sha256` value to the app's webhook endpoint, but replaces the header with `x-shopify-shop-domain: victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new` parses the forged headers and body: `request.shop == "victim-shop.myshopify.com"`, `request.hmac` unchanged from the valid capture [2](#0-1) .
4. `Utils::HmacValidator.validate(request)` recomputes `HMAC(api_secret_key, BODY)`, which still matches, since `to_signable_string` never included the shop [1](#0-0) .
5. `Registry.process` passes validation and calls `handler.handle(data: WebhookMetadata.new(... shop: "victim-shop.myshopify.com" ...))` [7](#0-6) , causing the app to act on `victim-shop`'s tenant record using attacker-supplied data.

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

**File:** lib/shopify_api/webhooks/webhook_handler.rb (L6-12)
```ruby
    class WebhookMetadata < T::Struct
      const :topic, String
      const :shop, String
      const :body, T::Hash[String, T.untyped]
      const :api_version, String
      const :webhook_id, String
    end
```

**File:** lib/shopify_api/auth/oauth/auth_query.rb (L33-43)
```ruby
        sig { override.returns(String) }
        def to_signable_string
          params = {
            code: code,
            host: host,
            shop: shop,
            state: state,
            timestamp: timestamp,
          }
          URI.encode_www_form(params)
        end
```
