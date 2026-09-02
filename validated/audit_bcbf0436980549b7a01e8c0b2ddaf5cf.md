Confirmed root cause: the HMAC signable string covers only `@raw_body`, while `shop`, `topic`, `webhook_id`, and `api_version` are read directly from headers without any cryptographic binding to the signature.I have sufficient evidence to confirm the vulnerability with exact file/line support.### Title
Webhook `shop` (tenant) identity is not covered by the HMAC signature, allowing shop-domain spoofing on genuine webhook deliveries - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC signature over the raw request body only, but the `shop` (tenant identifier), `topic`, `api_version`, and `webhook_id` values are read directly from HTTP headers that are never included in the signed payload. `Registry.process` validates only the body's HMAC and then forwards the header-derived, unauthenticated `shop` value to the app's `WebhookHandler#handle` as the trusted tenant identity.

### Finding Description
The identity binding that should hold is:
`hmac_signed_bytes == bytes_the_handler_trusts_as_the_tenant_identity`

In this gem it does not. `Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

Meanwhile `Request#shop` (and `topic`, `api_version`, `webhook_id`) are pulled straight from headers, with no cryptographic tie to the signature: [2](#0-1) 

`Registry.process` validates only `Utils::HmacValidator.validate(request)`, which in turn calls `to_signable_string` (body-only) against `request.hmac` (also header-derived): [3](#0-2) [4](#0-3) 

After this check passes, the untrusted header value `request.shop` is packaged into `WebhookMetadata` and handed to the host app's handler as the authoritative tenant identity: [5](#0-4) [6](#0-5) 

Because the app's shared `client_secret` (`api_secret_key`) is identical across every shop that has installed the app, a genuine webhook delivery received by *any* installed shop produces a body+HMAC pair that is valid for that secret regardless of which shop header accompanies it. An attacker who controls one legitimate installation (an "unprivileged internet user" with respect to every *other* tenant) can capture one of their own real webhook deliveries (valid `raw_body` + valid `hmac-sha256`) and replay it to the app's webhook endpoint with the `x-shopify-shop-domain` header rewritten to an arbitrary victim shop domain. `HmacValidator.validate` will report success because it never looks at the `shop` header, and `Registry.process` will hand the app's handler a `WebhookMetadata` claiming the event belongs to the victim shop.

This is the direct analog of the referenced bug class: a field that is *acted upon* (`shop`, used as the tenant/session key by the consuming handler) is not covered by the authenticity check (`hmac` over `raw_body` only), so the two notions of "shop" (asserted vs. cryptographically verified) diverge.

### Impact Explanation
Any handler that uses `WebhookMetadata#shop` to select a session, access token, database tenant, or to trigger tenant-scoped side effects (order processing, GDPR redact handling, data sync, etc.) can be made to act on/for the wrong tenant using data supplied by the attacker's own shop. This is a cross-tenant confusion vulnerability: it lets one merchant's install forge events "from" another merchant, without any credential belonging to the victim. This matches the Critical/High bucket of "cross-tenant access" via broken identity binding.

### Likelihood Explanation
Requires only: (1) attacker installs the target app in their own shop (a normal, low-privilege action any Shopify user with the app's install link can take), (2) attacker captures/produces at least one legitimate webhook to their own endpoint, and (3) attacker sends a crafted HTTP POST to the app's public webhook endpoint with the `shop-domain` header swapped and the original body/hmac intact. No knowledge of `client_secret`, no TLS interception, and no privileged account beyond a normal app install is needed. This is fully reachable through the gem's own public API (`Webhooks::Request.new` / `Registry.process`) as documented, not a misuse of undocumented behavior.

### Recommendation
Bind the tenant/topic/version/webhook-id headers into the value that is HMAC-verified, or otherwise require the app to independently corroborate `shop` (e.g., cross-check header shop against a shop recorded when the webhook subscription/session was created, keyed by `webhook_id`/subscription id rather than by the header alone). At minimum, document prominently that `WebhookMetadata#shop` is not authenticated and must be validated by the app before use.

### Proof of Concept
1. Attacker installs app in shop `attacker.myshopify.com`, configures webhook endpoint at `https://app.example.com/webhooks`.
2. Attacker triggers a real webhook (e.g., places an order), captures the HTTP POST body and `x-shopify-hmac-sha256` header.
3. Attacker crafts a new POST to `https://app.example.com/webhooks` with:
   - Same raw body (e.g., order JSON)
   - Same `x-shopify-hmac-sha256` header value
   - `x-shopify-shop-domain: victim.myshopify.com` (attacker-controlled)
   - `x-shopify-topic: orders/create` (from original)
4. App receives request, calls `Registry.process(request)`.
5. `HmacValidator.validate(request)` returns `true` (body+hmac match the shared secret, header shop is never checked).
6. `Registry.process` calls handler with `WebhookMetadata(shop: "victim.myshopify.com", body: {...}, ...)`.
7. Handler uses `data.shop` to look up victim's session/token and processes the attacker's order data as if it belongs to the victim. [7](#0-6)

### Citations

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
