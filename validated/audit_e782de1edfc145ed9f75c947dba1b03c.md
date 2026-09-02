This confirms the vulnerability. The `Webhooks::Request#to_signable_string` returns only `@raw_body` [1](#0-0) , while `shop` is read directly from the unauthenticated `shopify-shop-domain` / `x-shopify-shop-domain` header [2](#0-1) . `Utils::HmacValidator.validate` computes the signature only over `to_signable_string` (the raw body) [3](#0-2) , so the `shop` header is never covered by the HMAC. `Registry.process` trusts `request.shop` to attribute the webhook event to a tenant after only validating the body's HMAC [4](#0-3) .

### Title
Webhook `shop` header is not covered by HMAC verification, allowing cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` derives the tenant identity (`shop`) from the `x-shopify-shop-domain` HTTP header, but the HMAC signature that `Utils::HmacValidator` verifies only covers the raw request body, not the shop header. This breaks the intended identity binding: `shop header used to attribute the event == shop actually authenticated by the HMAC`. In reality, the HMAC authenticates only the body, and the shop attribution is accepted unauthenticated.

### Finding Description
`ShopifyAPI::Webhooks::Registry.process` is the entry point host applications call to process an incoming webhook. It validates the request solely via `Utils::HmacValidator.validate(request)` [5](#0-4) , which recomputes an HMAC over `request.to_signable_string`, i.e. only the raw JSON body [1](#0-0) , and compares it to the value pulled from the `hmac-sha256` header [6](#0-5)  and [7](#0-6) .

Once validation succeeds, `Registry.process` builds `WebhookMetadata` using `request.shop`, which is read straight from the `shop-domain` header without any cryptographic binding to the signed body [2](#0-1) , and dispatches it to the app's handler [8](#0-7) .

Because Shopify signs webhooks for every shop that installs an app using the same app-level `client_secret`, any merchant that has installed the app (an "unprivileged" party with respect to any other merchant) legitimately receives valid `(body, hmac)` pairs from Shopify for their own shop's events. Nothing in this gem prevents that body/hmac pair from being replayed to the same app's webhook endpoint with the `x-shopify-shop-domain` header rewritten to a different (victim) shop. `HmacValidator` still reports the request as valid because it never looks at the shop header, and `Registry.process` will hand the (attacker-supplied) shop value straight to the handler as the authenticated tenant. Any host application that relies on the gem's `shop`/`WebhookMetadata#shop` value as the sole tenant identity (which is the documented usage pattern) ends up processing data under the wrong tenant.

### Impact Explanation
This is a cross-tenant identity confusion: an attacker who is a legitimate but unprivileged user of the app (installed on their own store) can cause the host application to attribute genuine, HMAC-valid webhook traffic to an arbitrary victim shop domain of their choosing, since the shop identity is not bound to the signed payload. Depending on how the host app uses `WebhookMetadata#shop` (e.g., to look up per-shop access tokens/sessions or to trigger shop-scoped side effects), this can lead to cross-tenant data confusion or actions being performed against the wrong merchant's records — matching the "cross-tenant access" impact category.

### Likelihood Explanation
Any real merchant who installs the app automatically obtains valid signed webhook payloads for their own shop from Shopify — no leaked secrets, tokens, or privileged access are required. The only additional step is replaying that HTTP request to the app's webhook endpoint with a modified `shop-domain` header, which is fully within reach of an ordinary internet-facing HTTP client. This requires no access to the app's `client_secret` or any other party's credentials.

### Recommendation
Include the shop domain (and ideally topic/webhook-id) inside the value that is HMAC-verified, or otherwise cryptographically bind the `shop-domain` header to the signed body before trusting it — e.g., verify the shop domain against a shop already known/authenticated for the installation associated with the delivered webhook (via a stored offline session), rather than trusting the raw header value once the body-only HMAC succeeds.

### Proof of Concept
1. Attacker installs the target app on their own shop `attacker.myshopify.com` and receives a legitimate webhook from Shopify: body `B`, and headers including `x-shopify-shop-domain: attacker.myshopify.com`, `x-shopify-hmac-sha256: <valid HMAC over B>`.
2. Attacker sends a new HTTP request to the app's webhook endpoint with the exact same body `B` and the exact same `x-shopify-hmac-sha256` value, but replaces `x-shopify-shop-domain` with `victim.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new` parses the forged headers; `Utils::HmacValidator.validate` recomputes HMAC over `B` only [1](#0-0)  and it matches, so validation passes.
4. `Registry.process` calls `handler.handle(data: WebhookMetadata.new(topic:, shop: "victim.myshopify.com", body:, ...))` [8](#0-7) , causing the host application to process attacker-controlled body content under the victim shop's identity.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-13)
```ruby
      sig { override.returns(String) }
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
      end
```

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
