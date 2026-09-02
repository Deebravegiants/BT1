This confirms the finding. The webhook HMAC signature is computed only over the raw request body `to_signable_string` returning `@raw_body`, while the `shop` value used downstream comes from the `x-shopify-shop-domain`/`shopify-shop-domain` header, which is never included in the signed material.### Title
Webhook HMAC signature does not bind the `shop` header, allowing cross-tenant webhook spoofing via header substitution - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an incoming webhook solely by validating an HMAC over the raw HTTP body, but the `shop` identity that is subsequently handed to the app's webhook handler is read from an unsigned HTTP header. This breaks the intended binding `hmac-verified request == shop attributed to that request`, allowing a request with a genuine HMAC (computed with the app-wide `client_secret`) to be replayed with an attacker-chosen `shop-domain` header, causing the app to process the payload as if it belonged to a different, victim tenant.

### Finding Description
`ShopifyAPI::Webhooks::Request` implements `Utils::VerifiableQuery` (`lib/shopify_api/utils/verifiable_query.rb`), whose contract requires an `hmac` and a `to_signable_string`. For webhook requests, `to_signable_string` returns only the raw body: [1](#0-0) 

`shop` is instead pulled straight from the `shopify-shop-domain` / `x-shopify-shop-domain` header, with no cryptographic tie to the body or the HMAC: [2](#0-1) 

`Registry.process` validates only the body-derived HMAC and then trusts `request.shop` to construct the metadata passed to the app's handler: [3](#0-2) 

`HmacValidator.validate` computes the signature purely from `verifiable_query.to_signable_string` (the raw body) and the app's `Context.api_secret_key`: [4](#0-3) 

Critically, `Context.api_secret_key` is a single, app-wide (`client_secret`) value shared across *every* shop that has installed the app — it is not shop-specific. Any merchant who has installed the app on their own store legitimately receives webhooks from Shopify with a valid HMAC computed using this shared secret. Because the shop attribution lives entirely in an unsigned header, that same merchant can capture one of their own legitimate webhook deliveries (valid body + valid `hmac-sha256` header) and resend it to the app's webhook endpoint with the `shopify-shop-domain` header rewritten to point at a different (victim) shop. `HmacValidator.validate` will still pass, because it never inspects the `shop-domain` header, and the app's handler will process the payload believing it originated from the victim tenant — i.e., `shop authenticated (via HMAC) != shop attributed to the event`.

### Impact Explanation
This is a cross-tenant identity confusion: an unprivileged app user (any merchant with a legitimate install and a valid, but unrelated, webhook) can inject attacker-controlled webhook data attributed to an arbitrary victim shop into the host application's webhook handling logic (e.g., `shop/redact`, `customers/data_request`, order/product update handlers, etc.). Any host application logic that trusts `WebhookMetadata#shop` to select or mutate per-tenant data (a common and expected pattern, since this is exactly what the field is for) can be tricked into acting on the wrong tenant's records, satisfying the "cross-tenant access" criterion for a Critical-impact finding.

### Likelihood Explanation
The attacker only needs to be a legitimate, low-privilege user of the app (i.e., install it on any shop they control) to obtain one validly-signed webhook body/HMAC pair, and standard HTTP tooling to replay it with a modified header value — no access to `api_secret_key`, access tokens, or TLS interception is required. The vulnerability is fully within this gem's own request-validation code (`Request#to_signable_string`, `Request#shop`, `HmacValidator.validate`), not a misuse of a documented API by the host app.

### Recommendation
Bind the `shop` (and ideally `topic`/`webhook-id`) header values into the signed material verified by `HmacValidator`, e.g. by having `Request#to_signable_string` include a canonical representation of the shop header alongside the raw body, or by independently verifying `shop` against a known/expected value (such as an active session or subscription record) before invoking the handler, rather than trusting the raw header once the body-only HMAC check succeeds.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com`.
2. Shopify delivers a legitimate webhook to the app's endpoint with headers including `X-Shopify-Shop-Domain: attacker-shop.myshopify.com`, `X-Shopify-Hmac-Sha256: <valid-hmac-of-body>`, and some JSON body.
3. Attacker captures the raw body and the `X-Shopify-Hmac-Sha256` value unchanged, then resends the same body to the app's webhook endpoint but with `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
4. `ShopifyAPI::Utils::HmacValidator.validate(request)` in `lib/shopify_api/utils/hmac_validator.rb` recomputes the HMAC over `request.to_signable_string` (the unchanged raw body) and it matches — validation passes.
5. `ShopifyAPI::Webhooks::Registry.process` builds `WebhookMetadata.new(topic: request.topic, shop: request.shop, ...)` using `request.shop`, which now returns `"victim-shop.myshopify.com"`, and dispatches it to the app's handler as if the event genuinely came from the victim shop.

### Citations

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

**File:** lib/shopify_api/webhooks/registry.rb (L188-199)
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
