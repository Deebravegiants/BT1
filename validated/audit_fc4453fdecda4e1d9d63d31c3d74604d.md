### Title
Webhook `shop-domain` header is trusted without being covered by the HMAC signature, enabling cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body [1](#0-0) , while `shop`, `topic`, `webhook_id`, and `api_version` are all read straight from unauthenticated HTTP headers [2](#0-1) . `Registry.process` validates only that the HMAC matches the body, then hands the header-derived `shop` value directly to the app's handler [3](#0-2) .

### Finding Description
The identity binding that should hold is: `shop bound by HMAC == shop acted upon by handler`. Instead, the code verifies `HMAC(api_secret_key, raw_body)` but the `shop` (and `topic`/`webhook_id`) fields are taken from headers that are never part of the signed material [4](#0-3) .

Because `api_secret_key` is a single per-app secret shared across every shop that installs the app (not per-tenant), `HMAC(secret, body)` is identical for any two webhook deliveries that happen to carry the same body bytes, regardless of which shop they originated from. An unprivileged user who merely installs the app on their own shop (Shop A) receives genuine, correctly-signed webhook deliveries to their app endpoint. Nothing in this gem prevents that same request (raw body + valid `x-shopify-hmac-sha256`) from being re-submitted to the endpoint with the `x-shopify-shop-domain` (and/or `x-shopify-topic`) header rewritten to name a different shop (Shop B, the victim). `Utils::HmacValidator.validate(request)` still returns true, because it only checks the body [5](#0-4) , and `Registry.process` then invokes the handler with `shop: request.shop` taken straight from that unauthenticated header [3](#0-2) .

This is exactly the "field acted on but not covered by the HMAC" class: the gem's own webhook-processing API presents `shop` as a verified, trustworthy identity field to the host application (there is no other indication to the caller that `shop` is unauthenticated), while in fact only the body bytes are authenticated.

### Impact Explanation
This breaks the tenant boundary the HMAC is supposed to enforce. An attacker who is any ordinary merchant that installs the app (no special privilege, no leaked secrets, no access token, no TLS interception) can produce cross-tenant webhook deliveries that pass this gem's own HMAC validation but declare an arbitrary victim shop. Any host application that trusts `WebhookMetadata#shop` for tenant identification (nearly all of them, since that is the documented purpose of the field) can be driven to execute shop-scoped business logic — including mandatory-compliance topics like `shop/redact`, `customers/redact`, `customers/data_request`, or app-specific state changes (e.g. treating it as `app/uninstalled` for another merchant) — against a shop the attacker does not control. This is a cross-tenant access primitive, matching the report's underlying bug class (an operation performed against a victim's identity without any check binding the actor to that identity).

### Likelihood Explanation
The attack requires no credentials beyond installing the app as an ordinary merchant (an unprivileged internet user relative to other tenants), and no interaction with Shopify's servers beyond receiving one's own legitimate webhook once to obtain a valid `(body, hmac)` pair with a body simple/generic enough to also be a plausible payload for other shops/topics (many webhook bodies, e.g. minimal JSON payloads for compliance topics, are shop-agnostic or trivially replayable). The replay itself is a single crafted HTTP POST to the app's own public webhook endpoint with a modified `shop-domain` header.

### Recommendation
Include the `shop` (and ideally `topic`, `webhook_id`) values in the signed/verified material, or otherwise cryptographically bind them to the request before trusting them:
- Have `to_signable_string` incorporate the shop domain (and topic) in addition to the raw body, verified with a MAC that covers all header-derived fields the handler will rely on, or
- Require the host application to independently confirm `shop` against a known/installed-shop list before dispatching to handlers, and document clearly in `WebhookMetadata` that `shop` is not itself authenticated by the HMAC.

### Proof of Concept
```ruby
# Attacker owns "attacker-shop.myshopify.com" and has legitimately installed the app.
# They receive (or trigger, e.g. via a compliance-topic testing tool) one genuine webhook:
#   headers: {
#     "x-shopify-topic" => "customers/redact",
#     "x-shopify-hmac-sha256" => "<valid-signature-for-body>",
#     "x-shopify-shop-domain" => "attacker-shop.myshopify.com",
#   }
#   body: '{"shop_id":111,"shop_domain":"attacker-shop.myshopify.com","customer":{"id":1}}'
#
# Because HMAC only signs the raw body, and the body content the attacker fully controls
# the shape/timing of (or can reuse a minimal/generic body shared across topics), the
# attacker resubmits the exact same body+signature with the header changed:
headers = {
  "x-shopify-topic" => "customers/redact",
  "x-shopify-hmac-sha256" => "<same-valid-signature>",
  "x-shopify-shop-domain" => "victim-shop.myshopify.com",  # attacker-controlled, unauthenticated
}
request = ShopifyAPI::Webhooks::Request.new(raw_body: captured_body, headers: headers)
ShopifyAPI::Webhooks::Registry.process(request)
# => Utils::HmacValidator.validate(request) returns true (body signature matches)
# => handler.handle(data: WebhookMetadata.new(shop: "victim-shop.myshopify.com", topic: "customers/redact", ...))
# The host app's handler now performs a redaction/compliance action against victim-shop's data
# on the say of an attacker who never controlled victim-shop.
```

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
