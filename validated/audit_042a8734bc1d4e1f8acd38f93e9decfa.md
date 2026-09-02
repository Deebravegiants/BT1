Confirmed vulnerability class: HMAC-validated content excludes the `shop` field for webhook requests, unlike the OAuth callback path where `shop` is included in the signed string. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) 

### Title
Webhook `shop-domain` identity is not bound to the HMAC-verified request body, enabling cross-tenant webhook impersonation - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body, excluding the `shop-domain` header from the HMAC signature computation. `Utils::HmacValidator.validate` only proves that *some* body/HMAC pair was produced with the app's `client_secret`, not that the accompanying `shop` header actually corresponds to the shop that produced it. `Registry.process` then trusts `request.shop` verbatim and hands it to the app's webhook handler as the tenant identity, without any cross-check against the verified content.

### Finding Description
For the OAuth callback flow, the analogous `AuthQuery#to_signable_string` explicitly includes `shop` in the signed payload, so the shop cannot be swapped without invalidating the HMAC: [1](#0-0) 

For webhooks, however, `to_signable_string` signs only `@raw_body`, and `shop` is read from an unsigned HTTP header (`shopify-shop-domain` / `x-shopify-shop-domain`): [5](#0-4) 

`HmacValidator.validate` computes `HMAC(secret, to_signable_string)` and compares it to the header-supplied `hmac`, i.e. it only proves "this body was HMAC'd with the app's secret" — it says nothing about which shop the request is `for`: [6](#0-5) 

`Registry.process` then passes the *unverified* `request.shop` straight to the registered handler as the tenant identity that the app will act on (e.g. look up the shop's session/data): [3](#0-2) 

The identity-binding equality that should hold is: `shop verified by HMAC == shop the handler acts on`. Here that equality is broken: the HMAC only binds the *body bytes*, while the `shop` field consumed by the handler comes from an out-of-band header that carries no cryptographic binding to the signature at all.

Because the `client_secret` used to sign webhooks is the same for every shop that has the app installed (it's the app's secret, not a per-shop secret), an attacker who controls one shop with the app installed can:
1. Trigger any webhook topic/body on their own shop and capture the genuine `(raw_body, hmac)` pair Shopify sends.
2. Replay that exact body+HMAC to the app's webhook endpoint, but swap the `shopify-shop-domain` header to a victim shop's domain.
3. `HmacValidator.validate` still passes (it only checks the body/HMAC), and `Registry.process` invokes the handler with `data.shop` set to the victim's domain.

### Impact Explanation
This allows a low-privilege attacker (any merchant/developer who can install the app on their own store) to have arbitrary attacker-controlled webhook payloads processed by the app as though they originated from a different, victim shop/tenant — a cross-tenant data-integrity/impersonation issue. Depending on what the app's webhook handlers do with `data.shop` (e.g., updating shop records, triggering shop-scoped side effects), this can lead to cross-tenant state corruption or actions taken against the wrong tenant.

### Likelihood Explanation
Requires the attacker to have (or create) an app installation on a shop they control (a low bar — any merchant/dev store), and to control or predict a webhook payload for a topic the target app registers handlers for. No access token, secret, or privileged credential is needed; only the ability to send an HTTP request with a spoofed header to the app's public webhook endpoint together with a legitimately obtained body+HMAC pair.

### Recommendation
Include the shop domain (and ideally other identifying headers such as api-version/webhook-id) inside the HMAC-signed payload construction, or otherwise cryptographically bind the claimed `shop` to the verified body (e.g., by deriving the shop only from a value that is itself covered by the signature, or by requiring the handler layer to independently verify that the shop is one for which an active session/installation exists before trusting `data.shop`). At minimum, document that `request.shop` is unauthenticated and must not be trusted as a tenant boundary by consuming applications, or add a check in `Registry.process` cross-referencing the resolved shop against known/installed shops.

### Proof of Concept
```ruby
# Attacker's own shop: "attacker-shop.myshopify.com" (app installed here legitimately)
# Attacker captures a real Shopify webhook delivery for their own shop:
raw_body = '{"id":123,"note":"hello"}'
hmac = OpenSSL::HMAC.digest(OpenSSL::Digest.new("sha256"), app_client_secret, raw_body)
# (attacker knows this hmac because Shopify sent it to them for their own shop)

# Attacker now POSTs to the app's public webhook endpoint with a forged shop header:
headers = {
  "x-shopify-topic" => "orders/create",
  "x-shopify-hmac-sha256" => Base64.encode64(hmac),
  "x-shopify-shop-domain" => "victim-shop.myshopify.com", # <-- spoofed, not covered by hmac
}

request = ShopifyAPI::Webhooks::Request.new(raw_body: raw_body, headers: headers)
ShopifyAPI::Webhooks::Registry.process(request)
# HmacValidator.validate(request) => true, because it only checks HMAC(secret, raw_body)
# Handler receives WebhookMetadata with shop: "victim-shop.myshopify.com"
``` [3](#0-2)

### Citations

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

**File:** lib/shopify_api/webhooks/request.rb (L10-43)
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
