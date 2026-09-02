## Title
Webhook `shop` (tenant identity) Is Not Covered by the HMAC, Allowing Cross-Tenant Webhook Spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an incoming webhook solely by HMAC-validating the **raw request body**, then hands the **unauthenticated `shop-domain` header** to the app's handler as the tenant identifier. Because the HMAC signable string is the body only, any bytes carried in headers—most importantly the shop domain used for tenant routing—are never bound to the signature. An attacker who can obtain one genuine `(body, hmac)` pair from Shopify (e.g., by installing the app on their own store and receiving a real webhook) can resend that exact body/HMAC to the app's webhook endpoint with an arbitrary `shop-domain` header, and the request will still pass `HmacValidator.validate`.

### Finding Description
`Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`shop` is read from an unsigned header and exposed as a plain accessor: [2](#0-1) 

`Registry.process` validates the HMAC against the body only, then immediately trusts `request.shop` (a value never covered by that HMAC) to build the `WebhookMetadata` passed into the app's handler, which is the mechanism host apps use to know which tenant/shop the webhook belongs to: [3](#0-2) 

`HmacValidator.validate`/`validate_signature` confirm this: the signature check is computed purely over `verifiable_query.to_signable_string` (i.e. the body), never over headers such as `shop-domain`, `topic`, or `webhook-id`: [4](#0-3) 

This is the identity-binding break described in the report's bug class: the field acted upon downstream (`shop`, used to identify the tenant for handler dispatch) is not the field actually verified (only the JSON body bytes are verified). The equality that should hold — "shop bound in the verified bytes" == "shop acted on by the handler" — does not hold, since `shop` sits entirely outside `to_signable_string`.

### Impact Explanation
An attacker who legitimately installs the target app on their own (low-privilege) Shopify development/test store will receive genuine webhook deliveries for that store — real `(raw_body, x-shopify-hmac-sha256)` pairs signed with the app's `client_secret`. Because the signature never covers the `shop-domain` header, the attacker can replay that exact body and HMAC to the app's webhook endpoint while substituting any other shop's domain in the `shop-domain` header. `Registry.process` will accept it (HMAC check passes on the untouched body) and dispatch the handler with `shop` set to the victim's domain and `body` set to attacker-controlled content. Any host application that uses the passed `shop` for tenant-scoped operations (looking up/updating the victim's stored session or data, writing per-shop records, deciding which merchant's resources to touch) can be tricked into acting on the wrong tenant using attacker-supplied data — a cross-tenant access / data-integrity break carried entirely through this gem's `Webhooks::Registry`/`Request` API surface, without needing the victim's access token or `client_secret`.

### Likelihood Explanation
Requires only an internet-accessible install of the target app on any Shopify store the attacker controls (a normal, unprivileged onboarding flow) plus the ability to POST to the app's public webhook endpoint — both realistic, low-effort preconditions. No secrets, tokens, or elevated access are needed.

### Recommendation
Bind the shop (and ideally topic/webhook-id) into the signed content, or otherwise verify it out-of-band: at minimum, include `shop`, `topic`, and `webhook-id` in the value passed to `to_signable_string`/HMAC comparison (this would require a compatible scheme with Shopify's signing, e.g. verifying the header set as delivered by Shopify rather than trusting them independently), or require host apps to cross-check `request.shop` against an already-known/authenticated session/shop record before acting on webhook data, and document this requirement prominently since the gem currently implies HMAC success authenticates the whole request including `shop`.

### Proof of Concept
```ruby
# 1. Attacker installs the app on their own store "attacker.myshopify.com"
#    and receives a genuine webhook delivery:
raw_body = '{"id":123,"note":"legit payload from attacker store"}'
hmac = OpenSSL::HMAC.digest(OpenSSL::Digest.new("sha256"), app_secret, raw_body)
b64_hmac = Base64.encode64(hmac) # this is a REAL signature Shopify computed for attacker's shop

# 2. Attacker replays identical body+hmac but swaps shop-domain header to victim's shop
forged_headers = {
  "x-shopify-topic" => "orders/create",
  "x-shopify-hmac-sha256" => b64_hmac,          # unchanged, still valid for raw_body
  "x-shopify-shop-domain" => "victim-shop.myshopify.com", # NOT covered by HMAC
  "x-shopify-webhook-id" => "attacker-controlled-id",
  "x-shopify-api-version" => "2024-01",
}

request = ShopifyAPI::Webhooks::Request.new(raw_body: raw_body, headers: forged_headers)

# 3. HMAC validation succeeds because it only checks raw_body against app_secret
ShopifyAPI::Webhooks::Registry.process(request)
# => handler.handle(data: WebhookMetadata.new(shop: "victim-shop.myshopify.com", body: ..., ...))
# The handler now believes this authenticated data belongs to "victim-shop.myshopify.com".
```

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
