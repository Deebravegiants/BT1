### Title
Webhook shop attribution is not covered by the HMAC signature, allowing cross-tenant shop spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-signable content from the raw request body only, while the `shop` (tenant identity) is read from an unauthenticated HTTP header. `Registry.process` validates the HMAC and then hands the header-derived `shop` straight to the app's handler as trusted tenant context, breaking the intended binding between "bytes verified" and "bytes used to select the tenant."

### Finding Description
`Utils::HmacValidator.validate` verifies a request by recomputing the HMAC over `verifiable_query.to_signable_string` and comparing it to the received `hmac`: [1](#0-0) 

For webhooks, `Webhooks::Request#to_signable_string` returns only the raw body: [2](#0-1) 

But `shop` is parsed straight from the `shopify-shop-domain` / `x-shopify-shop-domain` HTTP header, which is not part of the signed content at all: [3](#0-2) 

`Registry.process` validates only the HMAC (which covers the body) and then constructs `WebhookMetadata` using this unauthenticated `request.shop`, passing it directly to the app-provided handler as the trusted tenant identifier: [4](#0-3) [5](#0-4) 

The binding that should hold is: `shop used to select/act on tenant data == shop authenticated by the HMAC`. In this implementation `hmac_verified_bytes = raw_body`, while `shop_used_for_tenant_routing = header["shop-domain"]`, i.e. `hmac_covers(bytes) ≠ bytes_that_determine_tenant`. Because Shopify signs webhook payloads for an app using the app's single shared `api_secret_key` across all shops that install the app (not a per-shop secret), any merchant/attacker who has (or creates) their own store with the app installed can capture a validly HMAC-signed `(body, hmac)` pair generated for their own shop, then replay it to the app's webhook endpoint with the `shop-domain` header rewritten to a victim shop's domain. `HmacValidator.validate` still succeeds (it never looked at the header), and the handler executes the attacker-supplied body under the identity of the victim shop.

### Impact Explanation
This is a cross-tenant confusion vector: an unprivileged internet user who can install the target app on any shop they control (a normal, self-service action) can forge the tenant-attribution header of an otherwise legitimately-signed webhook to make it appear to originate from a different merchant's shop. Any handler that trusts `WebhookMetadata#shop` (e.g., to look up/update per-shop records, deactivate/uninstall processing, sync inventory or orders) can be tricked into applying attacker-controlled payload contents to a victim shop's data — a cross-tenant access impact, which the rules list as Critical impact.

### Likelihood Explanation
Exploitation only requires: (1) installing the app on an attacker-controlled shop to legitimately receive a signed webhook (self-service, no special privilege), and (2) replaying the captured request to the app's webhook endpoint with a modified `shop-domain` header. No access to `api_secret_key`, access tokens, or the app's `client_secret` is required, and no TLS interception or credential theft is needed — this fits squarely within the unprivileged-internet-user threat model. Because `HmacValidator` never binds the header to the signature, the request passes verification unmodified.

### Recommendation
Include the shop domain (and ideally topic, api-version, webhook-id) as part of the HMAC-signable content for webhook requests, or otherwise cryptographically bind the header to the payload before it is trusted, matching how `Auth::Oauth::AuthQuery#to_signable_string` already includes `shop`, `host`, `code`, `state`, and `timestamp` in its signable string. At minimum, document loudly (and enforce in the gem) that `WebhookMetadata#shop` must never be trusted as tenant identity unless it is cross-checked against a shop the app installation actually recognizes, since it is not covered by the HMAC.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com` (a shop they control), which is a normal, unprivileged action supported by the app's OAuth flow.
2. Shopify sends a legitimately signed webhook to the app for `attacker-shop.myshopify.com`:
   - Headers: `x-shopify-shop-domain: attacker-shop.myshopify.com`, `x-shopify-hmac-sha256: <valid HMAC over raw_body>`, plus `topic`, etc.
   - Body: attacker fully controls content generated within their own shop (e.g., a fabricated order, product update, or customer payload triggered by their own store actions).
3. Attacker captures this `(raw_body, hmac)` pair and replays it to the app's webhook endpoint, but rewrites the `x-shopify-shop-domain` header to `victim-shop.myshopify.com`.
4. `Webhooks::Request#hmac` and `#to_signable_string` are unaffected by header changes, since `to_signable_string` is `@raw_body` only: [6](#0-5) 
5. `Utils::HmacValidator.validate` recomputes HMAC over `@raw_body` with the shared `api_secret_key` and it matches, so validation succeeds: [7](#0-6) 
6. `Registry.process` builds `WebhookMetadata` with `shop: request.shop` == `"victim-shop.myshopify.com"` (from the forged header) and dispatches it to the app's handler: [4](#0-3) 
7. Any handler logic keyed off `data.shop` (e.g., record lookups, data mutation, deactivation flows) now operates against `victim-shop.myshopify.com` using attacker-controlled body content — a cross-tenant data-integrity/confidentiality breach depending on handler logic.

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
