### Title
Webhook `shop` and `topic` identity headers are not covered by the HMAC signature, enabling cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` signs only the raw request body, while the tenant-identifying `shop-domain` and `topic` headers are read separately and passed unverified into the webhook handler. Anyone who can obtain one legitimately-signed `(body, hmac)` pair (e.g., by installing the app on their own store and receiving a real webhook) can replay that exact body/hmac while swapping the `shopify-shop-domain` (and/or `shopify-topic`) header to impersonate a different tenant, because `Utils::HmacValidator.validate` only checks the body against the signature and never binds the headers to it.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Request#shop` and `Request#topic` are read straight from HTTP headers with no cryptographic tie to the signed bytes: [2](#0-1) 

`Registry.process` verifies the HMAC over the request (which only covers the body) and then unconditionally trusts `request.shop` and `request.topic` when dispatching to the handler: [3](#0-2) 

`HmacValidator.validate_signature` only compares the computed signature of `to_signable_string` (the body) against the supplied `hmac`; it never incorporates `shop` or `topic`: [4](#0-3) 

This reproduces the same root-cause pattern as the referenced report (`safeDecimals` verifying only part of the data it later trusts as a whole): the code verifies bytes (`raw_body`) that are a subset of the bytes it actually acts on (`raw_body` + `shop` + `topic` headers), so verification and consumption are on different scopes of data. The binding that should hold is:

```
HMAC_valid(request) == HMAC_valid(raw_body, shop, topic)
```

but the implementation only checks:

```
HMAC_valid(request) == HMAC_valid(raw_body)
```

An attacker does not need the app's `client_secret`: any user of the app (e.g., an unprivileged merchant on their own trial shop, which is an "unprivileged internet user" relative to other merchants' data) can capture one real webhook delivery for their own shop (a legitimately signed `(raw_body, hmac)` pair sent to the app's public webhook endpoint) and then resend the identical body and `hmac-sha256` header to the same endpoint while substituting the `shopify-shop-domain` header (and optionally `shopify-topic`) with a different, victim shop's domain. `HmacValidator.validate` still returns `true` because it only re-derives the signature from `raw_body`, and `Registry.process` forwards the attacker-controlled `shop` value straight into `WebhookMetadata` for the handler.

### Impact Explanation
This breaks the tenant boundary the gem is supposed to enforce for webhook processing: an app's webhook handler receives data tagged with a `shop` (and/or `topic`) it cannot trust actually originated for that tenant, while believing it passed HMAC authentication. Any host application that uses `request.shop`/`request.topic` from `WebhookMetadata` to select tenant context, look up sessions/data, or make authorization decisions can be tricked into acting on/against the wrong tenant — i.e., cross-tenant access, which is explicitly a Critical-severity outcome per the impact taxonomy.

### Likelihood Explanation
Any user with legitimate access to install the app on their own store (a normal, unprivileged merchant) can generate one valid `(raw_body, hmac)` pair by simply triggering any webhook-eligible event on their own shop, then replay it against the public webhook endpoint with a forged `shop-domain`/`topic` header — no secret material or elevated privilege is required, only the ability to send an HTTP request the endpoint already exposes publicly (webhook endpoints are unauthenticated by design and rely solely on `HmacValidator`).

### Recommendation
Include the tenant-identifying headers in the signed payload, i.e. make `to_signable_string` (or the HMAC validation step) bind `shop-domain` and `topic` (and ideally `webhook-id`) together with the body, for example by hashing a canonical concatenation of these header values with the raw body, or by additionally comparing the accepted `shop`/`topic` against a value obtained through a channel the app trusts independently of these headers (e.g., cross-checking against the session that registered the webhook). At minimum, document that `WebhookMetadata#shop`/`#topic` are not authenticated on their own and must not be used for tenant selection without further verification.

### Proof of Concept
```ruby
# 1. Attacker (a normal merchant) installs the app on their own shop
#    "attacker-shop.myshopify.com" and lets it deliver one real webhook,
#    e.g. orders/create. They capture the raw POST body and the
#    "X-Shopify-Hmac-Sha256" header exactly as Shopify sent them.

raw_body = captured_body            # legitimately signed by Shopify
hmac_header = captured_hmac_header  # valid HMAC for raw_body only

# 2. Attacker replays the same body/hmac to the app's public webhook
#    endpoint, but swaps the shop-domain header to a victim shop.
headers = {
  "x-shopify-topic" => "orders/create",
  "x-shopify-hmac-sha256" => hmac_header,
  "x-shopify-shop-domain" => "victim-shop.myshopify.com", # forged
}

request = ShopifyAPI::Webhooks::Request.new(raw_body: raw_body, headers: headers)

# 3. HMAC validation still passes because it only checks raw_body:
ShopifyAPI::Utils::HmacValidator.validate(request) # => true

# 4. Registry.process hands the forged shop straight to the handler:
ShopifyAPI::Webhooks::Registry.process(request)
# handler.handle(data: WebhookMetadata.new(shop: "victim-shop.myshopify.com", ...))
``` [3](#0-2) [5](#0-4)

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
