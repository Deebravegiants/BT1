### Title
Webhook shop-domain and topic identity is trusted from unauthenticated HTTP headers while only the raw body is HMAC-verified - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an incoming webhook exclusively by validating the HMAC over the raw request body, but the `shop`, `topic`, `webhook_id`, and `api_version` values that are handed to the app's webhook handler as trusted identity/context are read directly from unauthenticated HTTP headers that are never included in the signed payload.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

The `hmac`, `shop`, `topic`, `webhook_id`, and `api_version` accessors are all sourced from `shopify_header`, i.e. directly from caller-supplied HTTP headers (`x-shopify-*` or `shopify-*`), none of which are part of the signed string: [2](#0-1) 

`Registry.process` validates the HMAC using `Utils::HmacValidator.validate(request)` — which internally calls `to_signable_string` (body only) — and then, once that single check passes, trusts `request.topic` and `request.shop` (both header-derived, unsigned) to route to a handler and to build the `WebhookMetadata` passed to the app's business logic: [3](#0-2) 

`HmacValidator.validate` computes the signature purely over `verifiable_query.to_signable_string`: [4](#0-3) 

The identity binding that should hold is: `shop authenticated by HMAC == shop consumed by the handler`. Here that equality is broken: the HMAC authenticates only the byte content of the body; the `shop` (and `topic`, `webhook_id`, `api_version`) that the handler receives via `WebhookMetadata` come from a completely separate, unauthenticated channel (headers). Any request whose body+signature pair is valid for the app's secret can have its `shop-domain`/`topic`/`webhook-id`/`api-version` headers swapped for arbitrary values without invalidating the signature check, because those header values never entered the signed string.

### Impact Explanation
This is a cross-tenant identity confusion: an attacker who can obtain one valid (body, HMAC) pair for the app's `client_secret` — e.g. a webhook the app genuinely receives for a shop the attacker installed the app on (a completely normal, unprivileged event) — can replay that exact body+HMAC to the app's webhook endpoint while substituting the `x-shopify-shop-domain` header for a victim shop's domain, or substituting `x-shopify-topic`/`x-shopify-webhook-id` to relabel the payload as a different, more privileged event (e.g. relabeling a benign topic as `app/uninstalled` or `shop/redact`). Downstream handlers that key persistence, deletion, or entitlement logic off `WebhookMetadata#shop`/`#topic` (which is the gem's documented, intended usage) will act on the wrong tenant. This satisfies the "cross-tenant access" impact bar, since the gem's own header-parsing contract is what silently mislabels the trust boundary, not merely an application bug — the gem exposes `shop`/`topic` as if they were part of the verified request.

### Likelihood Explanation
Any unprivileged internet user who can install the target app on a shop they control (the normal, free path to becoming an "authenticated" webhook sender for that one shop) automatically obtains valid (body, HMAC) pairs signed with the app's secret for topics they can trigger (e.g. any resource update in their own store). They can then freely relabel the `shop-domain`/`topic`/`webhook-id` headers on a replay, since the signature check in `HmacValidator.validate` (via `Request#to_signable_string`) never inspects those headers. No access token, `client_secret`, or privileged account is required — only ordinary use of the app as any merchant.

### Recommendation
Include the security-relevant headers (`shop-domain`, `topic`, `webhook_id`, `api_version`) in the signed/verified material, or otherwise cryptographically bind them to the body (e.g., verify them against values embedded in the payload, or require the host application to independently confirm `shop` against a known/installed-shop list before trusting `WebhookMetadata#shop`). At minimum, `Utils::HmacValidator` should validate that any header fields consumed for downstream authorization/business decisions are covered by the HMAC computation, not left as freely substitutable request metadata.

### Proof of Concept
1. Attacker installs the target Shopify app on their own store `attacker-shop.myshopify.com` and obtains the app's genuine, legitimately-delivered webhook HTTP request for any subscribed topic (e.g. `products/update`), capturing the raw body and the `x-shopify-hmac-sha256` header value — both are valid because Shopify itself computed the HMAC using the app's real `client_secret` for a webhook the attacker is entitled to receive.
2. Attacker resends this exact `raw_body` and `x-shopify-hmac-sha256` value to the app's public webhook endpoint, but modifies:
   - `x-shopify-shop-domain` to `victim-shop.myshopify.com`
   - `x-shopify-topic` to a different registered topic string (e.g. `app/uninstalled`), if the attacker wants to trigger different handler logic while keeping the same signed body.
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes the HMAC solely over `@raw_body` and finds it valid (unchanged from step 1).
4. The registry looks up the handler using the attacker-controlled `topic` header and invokes it with `WebhookMetadata.new(topic: request.topic, shop: request.shop, ...)`, both drawn from the attacker-controlled headers.
5. The app's handler executes business logic (e.g., deleting data, revoking entitlements, updating records) attributing the action to `victim-shop.myshopify.com`, even though nothing verified that this webhook actually originated for that shop. [3](#0-2) [5](#0-4)

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L1-63)
```ruby
# typed: strict
# frozen_string_literal: true

module ShopifyAPI
  module Webhooks
    class Request
      extend T::Sig
      include Utils::VerifiableQuery

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
