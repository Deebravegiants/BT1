## Analysis

The Shopify webhook HMAC verification in this gem authenticates only the request body, but the tenant identity (`shop`) used downstream to process the webhook is taken from an unauthenticated header, creating an unprivileged cross-tenant spoofing vector. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) 

### Title
Webhook `shop` identity is not bound by the HMAC signature, enabling cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`, so `Utils::HmacValidator.validate(request)` proves nothing about the `shop-domain` header. `Registry.process` trusts `request.shop` (the header) as the tenant identity passed to the app's handler, without that value ever being covered by the HMAC.

### Finding Description
`HmacValidator.validate` computes `HMAC(secret, verifiable_query.to_signable_string)` and compares it to the `hmac` attribute of the query object [5](#0-4) . For webhooks, `to_signable_string` is defined as `@raw_body` only [2](#0-1) , while `shop`, `topic`, `webhook_id`, and `api_version` are all pulled straight from HTTP headers with no cryptographic binding to the body or to each other [6](#0-5) .

`Registry.process` validates only the HMAC-over-body, then immediately routes using `request.shop` (unauthenticated) as the tenant key handed to the app's `WebhookHandler`: `handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop, body: request.parsed_body, ...))` [4](#0-3) .

This breaks the intended identity binding: `shop authenticated == shop used as tenant key`. Because a single `client_secret` is shared across every shop that installs the app, any merchant who legitimately installs the app receives real `(raw_body, hmac)` pairs for their own shop. That merchant (an unprivileged actor with respect to any *other* merchant's tenant) can resend the same body/HMAC to the app's webhook endpoint while substituting the `shopify-shop-domain` (or `x-shopify-shop-domain`) header with a victim shop's domain. `HmacValidator.validate` still succeeds because it never inspects the header, and `Registry.process` dispatches the handler with the attacker-chosen `shop` value, causing the host application to process data (e.g. mandatory `customers/redact`, `shop/redact` style handlers, or any custom per-shop persistence keyed by `shop`) under the wrong tenant.

### Impact Explanation
This is a cross-tenant identity binding break: an attacker who is a legitimate low-privilege installer for their own shop can cause the app to attribute a payload to a different merchant's shop identity, corrupting or misdirecting per-tenant state keyed by `shop` in the host application. This matches the "Critical - cross-tenant access" category, since the confused-deputy path lets one tenant's data or webhook triggers masquerade as another tenant's.

### Likelihood Explanation
Exploitation requires only that the attacker be an installed merchant of the target app (any app builder installing the gem is affected) and be able to POST an HTTP request with attacker-controlled headers and a previously-received legitimate `(raw_body, hmac)` pair to the app's public webhook endpoint. No access to `client_secret`, access tokens, or the victim's credentials is required — only capturing/replaying one's own legitimately-received webhook with a modified `shop-domain` header.

### Recommendation
Include the `shop` (and ideally `topic`, `webhook_id`) values inside the HMAC-signed content, or otherwise cryptographically bind the header-derived tenant identity to the signed body before calling `Registry.process`, so a modification of `shopify-shop-domain` invalidates the HMAC.

### Proof of Concept
1. Install the app on shop `attacker-shop.myshopify.com`; receive a legitimate webhook request with body `B` and header `shopify-hmac-sha256: HMAC(secret, B)` and `shopify-shop-domain: attacker-shop.myshopify.com`.
2. Replay the exact same body `B` and HMAC header to the app's webhook endpoint, but set `shopify-shop-domain: victim-shop.myshopify.com`.
3. `HmacValidator.validate(request)` succeeds (it only checks `HMAC(secret, B)` against `@raw_body`) [3](#0-2) .
4. `Registry.process` invokes the handler with `shop: "victim-shop.myshopify.com"` and the attacker's own body content [7](#0-6) , causing the host application to treat attacker-controlled data as belonging to `victim-shop.myshopify.com`.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-33)
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
```

**File:** lib/shopify_api/webhooks/request.rb (L35-38)
```ruby
      sig { override.returns(String) }
      def to_signable_string
        @raw_body
      end
```

**File:** lib/shopify_api/utils/hmac_validator.rb (L12-21)
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
