### Title
Webhook HMAC signature only covers the request body, not the `shop`, `topic`, or `webhook-id` headers - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-verifiable payload solely from the raw request body, while `shop`, `topic`, and `webhook_id` are read directly from unauthenticated HTTP headers. `Utils::HmacValidator.validate` only proves that the *body* bytes were signed by Shopify with the app's secret — it proves nothing about which shop, topic, or webhook the signature was meant for. Any holder of one legitimately-signed webhook body/HMAC pair (which any merchant using the app can obtain from their own store's webhook deliveries) can resubmit that exact body with a different `shop-domain` header and have it pass validation as if it originated from another tenant.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

but `shop`, `topic`, and `webhook_id` are pulled from headers that are never part of the signed data: [2](#0-1) 

`HmacValidator.validate` computes the signature purely from `verifiable_query.to_signable_string` (i.e. the body) and compares it with `OpenSSL.secure_compare`: [3](#0-2) 

`Webhooks::Registry.process` trusts the validated request and forwards `request.shop`, `request.topic`, and `request.webhook_id` straight to the app's handler as the tenant/action context, with no additional binding check: [4](#0-3) 

The equality the gem is implicitly relying on is:
`bytes verified by HMAC (raw_body)` == `bytes the application acts on (raw_body + shop + topic + webhook_id)`

This equality does not hold: the HMAC only authenticates the body, so `shop`/`topic`/`webhook_id` are attacker-controlled from the perspective of this validation. Contrast this with `Auth::Oauth::AuthQuery#to_signable_string`, which correctly folds `shop`, `host`, `code`, `state`, and `timestamp` into the signed string: [5](#0-4) 

showing that the webhook path is inconsistent with the OAuth path's binding discipline.

### Impact Explanation
An unprivileged user who merely operates their own shop with the app installed will legitimately receive real webhook deliveries (body + valid HMAC) for their own store from Shopify. Because the signature never binds `shop-domain`, that same person can replay the identical body/HMAC pair to the app's webhook endpoint while substituting a victim shop's domain in the `shopify-shop-domain` header (and/or a different topic/webhook-id). `HmacValidator.validate` will still return `true`, since it only checks the body bytes, and `Webhooks::Registry.process` will hand the forged `shop`/`topic` to the app's handler as if Shopify itself certified that mapping. Depending on what the host application does with `WebhookMetadata#shop` (e.g., looking up/deleting the victim's stored session, marking the victim's app as uninstalled on `app/uninstalled`, or triggering GDPR data-redaction flows on `customers/redact`/`shop/redact`), this is a cross-tenant integrity/data violation: one tenant can trigger tenant-scoped side effects attributed to another tenant using a credential (the shared `api_secret_key`-derived HMAC) that was never meant to authorize that assignment.

### Likelihood Explanation
Low-to-moderate: exploitation requires the attacker to control (or observe) at least one shop that has the target app installed so they can obtain a genuine signed webhook body, and it requires the host application to trust `WebhookMetadata#shop`/`#topic` for security-relevant decisions without independently re-verifying the shop (which is the documented, expected usage pattern shown in the gem's own docs/tests). No secrets, tokens, or privileged access are needed beyond ordinary merchant-level access to install the app on a shop.

### Recommendation
Include `shop`, `topic`, and `webhook_id` (and any other header fields the handler relies on) in the HMAC-signed payload used by `Request#to_signable_string`, matching the pattern already used in `Auth::Oauth::AuthQuery`. If Shopify's actual webhook HMAC scheme only signs the body (per Shopify's webhook spec), then `Webhooks::Registry`/`Request` should not expose `shop`/`topic`/`webhook_id` as trusted, authenticated fields to consumers without documenting that they are unauthenticated and must be corroborated against the app's own installation records before being used for tenant-scoped actions.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com` and receives a legitimate webhook, e.g. `orders/create` with body `B` and header `shopify-hmac-sha256: H` (valid HMAC of `B` under the shared `api_secret_key`).
2. Attacker sends the following forged request to the app's webhook endpoint:
```
POST /webhooks
shopify-topic: app/uninstalled          # or customers/redact, etc.
shopify-hmac-sha256: H                  # unchanged, still valid because only body is signed
shopify-shop-domain: victim-shop.myshopify.com   # forged victim tenant
Body: B                                  # unchanged legitimate body
```
3. `ShopifyAPI::Utils::HmacValidator.validate(request)` returns `true` because it only re-computes HMAC over `B`: [6](#0-5) 
4. `ShopifyAPI::Webhooks::Registry.process(request)` dispatches to the registered handler for `app/uninstalled` (or whichever topic was forged) with `shop: "victim-shop.myshopify.com"`, even though Shopify never issued a webhook for that shop/topic combination: [4](#0-3)

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
