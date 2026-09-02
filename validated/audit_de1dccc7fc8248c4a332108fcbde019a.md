### Title
Webhook `shop` identity is not covered by the HMAC signature, allowing cross-tenant shop spoofing on otherwise-valid webhook payloads - (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/webhooks/registry.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating the HMAC of the raw request body via `Utils::HmacValidator.validate(request)`. The `shop` value that is then handed to the app's handler as the tenant identity is read from the `shopify-shop-domain`/`x-shopify-shop-domain` HTTP header, which is never part of the signed content.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`shop` (and `topic`, `webhook_id`, `api_version`) are pulled straight from HTTP headers that are not included in that signable string: [2](#0-1) 

`HmacValidator.validate` verifies `verifiable_query.hmac` against `HMAC(secret, verifiable_query.to_signable_string)` only — i.e. only the body bytes are authenticated: [3](#0-2) 

`Registry.process` accepts the request once the body HMAC checks out, and then forwards `request.shop` (the unauthenticated header value) as the tenant identity to the app-provided handler, along with `request.parsed_body`: [4](#0-3) [5](#0-4) 

This breaks the identity binding `HMAC-authenticated bytes == bytes acted upon`: the bytes verified by HMAC are `raw_body` only, but the field actually used to select/attribute the tenant (`shop`) is unverified header data. Any party capable of producing one genuine `(raw_body, hmac)` pair for the app's `client_secret` — e.g., an attacker who installs the target app on their own Shopify development/trial store and receives real webhooks Shopify sends them — can replay that exact `raw_body`+`hmac` to the app's webhook endpoint while substituting the `shopify-shop-domain` header with a victim shop's domain. The HMAC still validates (it only checks the body), yet `Registry.process` attributes the (attacker-controlled) body to the victim shop's `WebhookMetadata`.

### Impact Explanation
This is a cross-tenant identity-binding failure comparable in class to the `TrufVesting` bug: a value that governs a critical decision (`shop`/tenant selection) is exempted from the same check that is supposed to prove authenticity of the whole message (the HMAC). Any host application that persists or acts on `WebhookMetadata#shop` (e.g., storing order/customer data keyed by shop, running mandatory GDPR handlers like `shop/redact` or `customers/redact` keyed by shop) can be made to apply attacker-influenced webhook content to a different, victim tenant, without the attacker ever possessing the app's `client_secret` or any victim credentials. This matches the "cross-tenant access" Critical-impact category since the gem's own signature-validation contract silently permits shop-spoofing.

### Likelihood Explanation
Exploitation requires the attacker to obtain one legitimately-signed `(body, hmac)` pair from Shopify for the target app (trivially achievable for any app that can be installed on a free/dev store and that sends webhooks the attacker can trigger with attacker-chosen content, e.g. order or product webhooks created by the attacker in their own store) and then freely forge the `shopify-shop-domain` header when replaying it to the app's public webhook endpoint. No secret material, TLS interception, or privileged access is needed — only the ability to send an HTTP request with attacker-chosen headers, which is exactly the "unprivileged internet user" scenario this analysis targets.

### Recommendation
Include `shop` (and ideally `topic`, `webhook_id`, `api_version`) in the HMAC-signed content, or otherwise cryptographically bind the header-derived `shop` to the payload before it is exposed as `WebhookMetadata#shop`. At minimum, `Utils::VerifiableQuery`/`Webhooks::Request#to_signable_string` should incorporate the shop domain (matching how Shopify's own HMAC verification recommendations expect the full canonical request, not just the body) so that `Registry.process` cannot deliver a validated payload under an attacker-chosen tenant identity.

### Proof of Concept
1. Attacker installs the target Shopify app on their own store `attacker.myshopify.com` and creates an order, causing Shopify to send a genuine `orders/create` webhook with header `X-Shopify-Shop-Domain: attacker.myshopify.com`, some `raw_body`, and a correctly computed `X-Shopify-Hmac-Sha256` for that `raw_body` using the app's real `client_secret` (attacker never sees the secret, only the resulting header value).
2. Attacker intercepts/replays this exact HTTP request to the app's public webhook endpoint, but rewrites the `X-Shopify-Shop-Domain` header to `victim.myshopify.com`, leaving `raw_body` and `X-Shopify-Hmac-Sha256` untouched.
3. `ShopifyAPI::Webhooks::Request.new` parses headers/body; `Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes HMAC over `raw_body` only and succeeds because the body was never modified: [6](#0-5) 
4. `handler.handle` is invoked with `WebhookMetadata.new(shop: "victim.myshopify.com", body: <attacker-controlled JSON>, ...)`, so the host application processes attacker-supplied data as if it originated from the victim's authenticated shop.

Note: I could not find a `Webhooks::CliTools` or reverse-proxy component in the indexed portion of this repo that might add extra header binding at a different layer; if such code exists in un-indexed files it should be checked as well, but based on the available source, `Request`/`Registry`/`HmacValidator` are the complete authentication path for webhooks.

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
