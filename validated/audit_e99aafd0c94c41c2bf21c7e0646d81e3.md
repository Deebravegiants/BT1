### Title
Webhook `shop` (tenant) identity is not covered by the HMAC signature, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/webhooks/registry.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates a webhook by validating the HMAC over the raw request body only, then dispatches the event to the app's handler using the `shop` value taken from the `X-Shopify-Shop-Domain` header — a field that is never part of the signed payload. Because the app's webhook secret (`api_secret_key`) is shared across every shop that installs the app, any merchant that has installed the app can capture one of their own legitimately-signed webhook deliveries and replay it against the app's webhook endpoint with the `shop-domain` header changed to a different (victim) shop, producing a request that passes HMAC validation while being attributed to a shop the attacker does not control.

### Finding Description
`Webhooks::Request#to_signable_string` returns only the raw HTTP body: [1](#0-0) 

`shop` is read straight from the (unsigned) header: [2](#0-1) 

`Registry.process` validates the HMAC against that signable string, then immediately trusts `request.shop` to build the `WebhookMetadata` handed to the app's handler: [3](#0-2) 

`HmacValidator.validate` (and `validate_signature`) only ever compares `verifiable_query.to_signable_string` against the computed signature — for `Webhooks::Request` this string is the raw body, so `shop` never enters the signed material: [4](#0-3) 

The identity binding that should hold is: **shop authenticated by HMAC == shop the payload is processed for**. Because the header carrying the shop is outside the signed bytes, this equality does not hold — `verified_bytes (body only)` != `bytes acted on (body + shop header)`.

Critically, the HMAC key (`Context.api_secret_key`) is the app's single client secret, identical for every merchant shop that installs the app. Any one merchant's app installation therefore legitimately possesses `(body, hmac)` pairs signed with that shared secret from their own genuine webhook deliveries. Since the signature verification never checks which shop the header claims, that same `(body, hmac)` pair remains valid no matter what `shop-domain` header value accompanies it.

### Impact Explanation
An unprivileged merchant who has installed the app (i.e., has no privileged access to any other tenant) can take a webhook delivery originally addressed to their own shop and resend it to the app's webhook endpoint with the `x-shopify-shop-domain`/`shopify-shop-domain` header changed to an arbitrary victim shop domain. `Registry.process` will accept it (HMAC checks out) and invoke the registered handler with `WebhookMetadata#shop` set to the spoofed victim shop, causing the app to process attacker-controlled webhook data as if it originated from — and pertains to — a different tenant. This is a cross-tenant integrity violation: the app's business logic (order/customer/product handling, GDPR/mandatory webhook processing, cache/session updates keyed by shop, etc.) will be executed under a false tenant identity supplied entirely by the attacker.

### Likelihood Explanation
Exploitation requires only that the attacker be a legitimate installer of the target app on any shop (a normal, unprivileged install) and standard HTTP tooling to replay a captured request with one header changed. No access to `api_secret_key`, access tokens, or any other shop's credentials is required — this is squarely an internet-reachable action available to any app-installing merchant.

### Recommendation
Bind the shop identity into the signed material, or otherwise cryptographically tie the header-provided shop to the verified payload, before trusting it:
- Compute/verify the HMAC over a canonical string that includes the `shop-domain` (and `topic`/`webhook-id`) header values in addition to the raw body, rejecting requests where the header-derived shop was not part of what Shopify actually signed, or
- Cross-check the header-provided shop against an independent trust anchor (e.g., look up the webhook/shop pairing via a signed API call, or require the app's own webhook endpoint to be scoped per-shop) rather than trusting the header value alone once HMAC validation has passed.

### Proof of Concept
1. App is installed on attacker-controlled shop `attacker.myshopify.com`; attacker's server receives a normal webhook, e.g.:
```
POST /webhooks
x-shopify-topic: orders/create
x-shopify-hmac-sha256: <valid-hmac-of-raw-body>
x-shopify-shop-domain: attacker.myshopify.com
x-shopify-webhook-id: ...
<raw-body>
```
2. Attacker resends the identical request to the app's webhook endpoint, changing only the shop header:
```
POST /webhooks
x-shopify-topic: orders/create
x-shopify-hmac-sha256: <same valid hmac, body unchanged>
x-shopify-shop-domain: victim.myshopify.com
x-shopify-webhook-id: ...
<same raw-body>
```
3. `Utils::HmacValidator.validate` succeeds because it only checks the (unchanged) raw body against the (unchanged) HMAC — see [5](#0-4) .
4. `Registry.process` dispatches to the app's handler with `shop: "victim.myshopify.com"` — see [6](#0-5)  — even though the payload actually originated from, and was signed for, `attacker.myshopify.com`.

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
