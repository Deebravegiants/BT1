### Title
Webhook tenant identity (`shop`) is not covered by the HMAC signature, allowing cross-tenant webhook forgery - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` computes the HMAC-verifiable signable string from the raw HTTP body only, while the shop identity, topic, webhook id and API version used to route and attribute the webhook are read from unsigned HTTP headers. `HmacValidator` only proves the body is authentic, not which shop it belongs to, so an attacker who has captured any one valid `(body, hmac)` pair (e.g. from a webhook Shopify sent for their own store) can replay it to the app's public webhook endpoint with a forged `shop-domain` header and the handler will process it as if it came from a different, victim tenant.

### Finding Description
`Webhooks::Request#to_signable_string` returns only the raw body: [1](#0-0) 

The `shop`, `topic`, `webhook_id`, and `api_version` fields are parsed straight from HTTP headers and are never part of the signed bytes: [2](#0-1) 

`Utils::HmacValidator.validate` verifies `computed_signature` against `verifiable_query.hmac` using only `to_signable_string` (i.e., the body): [3](#0-2) 

`Registry.process` calls this validator and, once it passes, unconditionally trusts `request.shop` and `request.topic` (unsigned headers) to build the metadata handed to the app's handler: [4](#0-3) 

This reproduces the report's bug class exactly: a field that is *acted on* (`shop`, used as the tenant identity for the webhook) is not covered by the cryptographic check that is supposed to authenticate the message. The equality that should hold — `bytes verified == bytes/fields used to identify the tenant` — is broken: only `raw_body` is verified, but `shop`/`topic`/`webhook_id` headers are used to attribute and route the payload.

### Impact Explanation
Any entity capable of obtaining one legitimate `(raw_body, hmac)` pair for the app — trivially achievable by any unprivileged merchant who installs the public app on their own development/test store and receives one real webhook — can replay that exact body+HMAC to the app's public webhook endpoint while substituting the `shop-domain` (and/or `topic`) header for a different, victim shop. Since `HmacValidator` never inspects headers, the forged request passes signature verification and is delivered to the app's webhook handler tagged as belonging to the victim shop. This is a cross-tenant confusion/isolation break: the app processes attacker-supplied event data under another tenant's identity, which can corrupt per-shop state, trigger shop-scoped side effects (installs/uninstalls, order/inventory sync, etc.) attributed to the wrong merchant. This maps to the "cross-tenant access" impact category.

### Likelihood Explanation
Exploitation requires no privileged credentials, access tokens, or the app's `client_secret` — only the ability to install the app once on an attacker-owned store (a normal, unprivileged action any Shopify user can take) to harvest one authentic body/HMAC pair, and the ability to send an HTTP POST with custom headers to the app's known public webhook URL. No cryptographic secret needs to be broken since the signature check never covers the header the attack manipulates.

### Recommendation
Include the shop domain (and ideally the topic/webhook id/api-version) in the signed/verified bytes, or independently bind the verified body's shop identity by cross-checking it against the shop derived from an authenticated session/lookup rather than trusting the `X-Shopify-Shop-Domain` header outright. At minimum, `Registry.process` should reject requests whose header-derived `shop` cannot be corroborated by a value inside the signed payload or by a separately verified access-token/session binding.

### Proof of Concept
1. Attacker installs the target Shopify app on their own store `attacker.myshopify.com` and registers/receives a webhook for some topic; Shopify sends `POST /webhooks` with body `B` and header `X-Shopify-Hmac-Sha256: H` (computed by Shopify over `B` using the shared `client_secret`), plus `X-Shopify-Shop-Domain: attacker.myshopify.com`.
2. Attacker captures `(B, H)`.
3. Attacker sends their own `POST /webhooks` request directly to the app's public endpoint with identical body `B` and header `X-Shopify-Hmac-Sha256: H`, but sets `X-Shopify-Shop-Domain: victim.myshopify.com`.
4. `ShopifyAPI::Webhooks::Request.new` parses headers and body; `Registry.process` calls `Utils::HmacValidator.validate(request)` [5](#0-4) , which succeeds because it only recomputes the HMAC over `B` — identical to what Shopify actually signed.
5. The handler receives `WebhookMetadata.new(topic: ..., shop: "victim.myshopify.com", body: ..., ...)` [6](#0-5)  and processes attacker-controlled data as if it originated from the victim shop.

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
