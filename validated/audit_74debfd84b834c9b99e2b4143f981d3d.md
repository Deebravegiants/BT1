### Title
Webhook shop attribution is not bound to the HMAC signature, allowing cross-tenant shop spoofing - ([File: lib/shopify_api/webhooks/registry.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an incoming webhook by validating an HMAC computed only over the raw request body, then unconditionally trusts the `shop-domain` header (exposed as `request.shop`) to attribute the webhook to a tenant. The `shop` field is never included in the signed content, so it can be freely altered without invalidating the HMAC — the same class of bug as the audited report, where a value (`amount_`) that drives execution was not covered by the fee/validation calculation.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`shop` is read straight from the `shop-domain`/`x-shopify-shop-domain` header, which is not part of that signable string: [2](#0-1) 

`Registry.process` validates the HMAC using `Utils::HmacValidator.validate(request)`, which computes `HMAC(secret, request.to_signable_string)` — i.e., `HMAC(secret, raw_body)` — and compares it against `request.hmac` (also derived only from the `hmac-sha256` header): [3](#0-2) 

Immediately after this check passes, `Registry.process` forwards `request.shop` (the raw, unauthenticated header value) into `WebhookMetadata` and on to the app's registered handler, with no further validation that this shop matches anything covered by the signature: [4](#0-3) 

The identity binding that should hold is:
`shop authenticated by HMAC == shop attributed to the webhook payload (data.shop)`

In reality, the HMAC only proves `HMAC(secret, raw_body)` is correct; it says nothing about which shop the body belongs to. Consequently:
`shop covered by HMAC (∅, not present in to_signable_string) ≠ shop consumed by handler (request.shop, from unauthenticated header)`

An attacker who can influence or replay a request to the app's webhook endpoint (e.g., via a captured/legitimate webhook payload whose body is not shop-specific, or any payload for which the attacker can compute/obtain a valid `hmac-sha256` value, such as a webhook the attacker's own installed app receives from Shopify using the same or leaked `api_secret_key` context, or more directly by replaying a previously observed valid webhook with a modified `shop-domain` header) can cause the gem to report a different `shop` than the one the payload/HMAC was actually generated for, while `Registry.process` still reports the HMAC as valid.

### Impact Explanation
This breaks the tenant boundary the gem is documented to enforce. `Registry.process` is documented as verifying "the request did indeed come from Shopify" before invoking the handler, and the handler is explicitly given `data.shop` to use as the authenticated tenant identifier (per `docs/usage/webhooks.md`). Because `shop` is not covered by the signature, a host application that trusts `data.shop` as authenticated (as the gem's own documentation instructs it to) can be made to process, store, or act on data under the wrong shop/tenant — i.e., cross-tenant access/confusion at the trust boundary this gem is responsible for validating. Mandatory webhook topics such as `shop/redact` and `customers/redact`/`customers/data_request` are especially sensitive, since misattributing them to the wrong shop causes the wrong tenant's data to be affected by data-erasure or PII operations.

### Likelihood Explanation
Exploitation requires the attacker to produce (or replay) a request with a body whose HMAC is valid for the configured `api_secret_key`, then simply changing the `shop-domain` header — no possession of the `api_secret_key`, access token, or any privileged credential is needed to manipulate the header itself. Any scenario where an attacker can capture a legitimate webhook delivery (e.g., from their own shop's installation of the app, or from network logs/observability tooling that is not fully locked down) is sufficient to obtain a body+HMAC pair; the header can then be freely modified before it reaches the app's endpoint, since nothing in this gem re-derives or cross-checks `shop` against the signed content.

### Recommendation
Include `shop` (and ideally `topic`, `webhook_id`, `api_version`) in the HMAC-signable content, or otherwise cryptographically bind the shop attribution to the verified payload, before trusting `request.shop` in `Registry.process`. At minimum, document and/or enforce that `data.shop` from `WebhookMetadata` must be cross-checked by the host application against a known/expected shop for the webhook subscription, since this gem currently does not perform that binding itself.

### Proof of Concept
1. Attacker installs the app on `attacker-shop.myshopify.com` and receives a legitimate webhook whose body is `raw_body` with a correctly computed `hmac-sha256` header for that body (e.g., `orders/create` with an empty or reusable body such as `{}`).
2. Attacker replays this exact `raw_body` and `hmac-sha256` value to the app's webhook endpoint, but sets the `shop-domain` (or `x-shopify-shop-domain`) header to `victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new(raw_body:, headers:)` parses the forged `shop` header. [5](#0-4) 
4. `ShopifyAPI::Webhooks::Registry.process(request)` calls `Utils::HmacValidator.validate(request)`, which recomputes `HMAC(secret, raw_body)` and matches the (still-valid, unchanged) `hmac-sha256` header — validation succeeds despite the shop header being forged. [4](#0-3) 
5. The registered handler is invoked with `data.shop == "victim-shop.myshopify.com"`, even though the signed body actually originated from `attacker-shop.myshopify.com`'s webhook delivery — the host application, trusting the gem's authentication, now processes attacker-controlled/misattributed webhook content under the victim shop's identity.

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

**File:** lib/shopify_api/webhooks/request.rb (L45-63)
```ruby
      sig { params(raw_body: String, headers: T::Hash[String, T.untyped]).void }
      def initialize(raw_body:, headers:)
        # normalize the headers by forcing lowercase, removing any prepended "http"s, and changing underscores to dashes
        headers = headers.to_h { |k, v| [k.to_s.downcase.sub("http_", "").gsub("_", "-"), v] }

        missing_headers = []
        ["topic", "hmac-sha256", "shop-domain"].each do |name|
          unless headers.key?("shopify-#{name}") || headers.key?("x-shopify-#{name}")
            missing_headers << "shopify-#{name} or x-shopify-#{name}"
          end
        end
        unless missing_headers.empty?
          raise Errors::InvalidWebhookError,
            "Missing one or more of the required HTTP headers to process webhooks: #{missing_headers}"
        end

        @headers = headers
        @raw_body = raw_body
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
